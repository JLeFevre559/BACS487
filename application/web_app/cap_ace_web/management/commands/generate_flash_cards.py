"""
Generate true/false flash cards for financial literacy education.
"""
import json
import random
from typing import List, Dict, Any

from django.db import transaction
from ...models import FlashCard, CATEGORIES, DIFFICULTIES
from .base_generation_command import BaseGenerationCommand
from .ai_utils import extract_json_from_response, is_similar_text

# AI prompt template for generating flash cards
AI_PROMPT = """
Generate EXACTLY {num} true/false flash cards about {category_display} for teaching financial literacy. Do not generate more or fewer than {num} flash cards.

For each flash card, include:
1. A statement about financial literacy that is either true or false
2. A boolean value indicating whether the statement is true (true) or false (false)
3. A detailed explanation/feedback explaining why the statement is true or false
4. Difficulty level (B for Beginner, I for Intermediate, A for Advanced)

Ensure that each flash card:
- Tests understanding, not just recall
- Has a clear, unambiguous statement
- Is engaging and relevant for teaching financial concepts
- Has approximately 50% true statements and 50% false statements across all cards
- Is written at an appropriate difficulty level ({difficulty_display})

Return your response as a valid JSON array with EXACTLY {num} objects in this format:
[
  {{
    "question": "A good budget should account for savings as a regular expense.",
    "answer": true,
    "feedback": "This statement is true. Treating savings as a regular expense in your budget (sometimes called 'paying yourself first') ensures that you consistently set aside money for future needs and goals before spending on discretionary items.",
    "difficulty": "Difficulty level here (B, I, A)",
    "category": "{category_code}"
  }},
  ... additional flash cards ...
]

The final JSON array MUST contain EXACTLY {num} flash card objects, no more and no less.

Only include the valid JSON array in your response, with no additional explanations, preambles, or postscripts.
"""


class Command(BaseGenerationCommand):
    help = 'Generate flash cards using AI and add them to the database'
    content_type_name = "flash cards"
    default_batch_size = 10
    system_message = "You are a financial education expert. Generate true/false flash cards for teaching financial literacy concepts."
    
    def add_model_arguments(self, parser):
        """Add model-specific arguments."""
        parser.add_argument(
            '--category', 
            type=str, 
            choices=[code for code, _ in CATEGORIES],
            help='Category of flash cards to generate (will use random category if not specified)'
        )
        parser.add_argument(
            '--difficulty', 
            type=str, 
            choices=[code for code, _ in DIFFICULTIES],
            default='B',
            help='Difficulty level of flash cards to generate'
        )
    
    def process_options(self, options: Dict[str, Any], use_random: bool = False) -> Dict[str, Any]:
        """Process command options and return parameters for prompt formatting."""
        from ...models import CATEGORIES, DIFFICULTIES
        
        difficulty = options['difficulty']
        
        # If a category is specified and we're not forcing random, use that category
        if 'category' in options and options['category'] is not None and not use_random:
            category = options['category']
            self.stdout.write(self.style.SUCCESS(f"Using specified category: {category}"))
        else:
            # Either no category specified or we're forcing random - select random category
            category_codes = [code for code, _ in CATEGORIES]
            category = random.choice(category_codes)
            self.stdout.write(self.style.SUCCESS(f"Using randomly selected category: {category}"))
        
        # Find the display name for the category
        category_display = next((name for code, name in CATEGORIES if code == category), "Budgeting")
        
        # Find the display name for the difficulty
        difficulty_display = next((name for code, name in DIFFICULTIES if code == difficulty), "Beginner")
        
        return {
            'category_code': category,
            'category_display': category_display,
            'difficulty': difficulty,
            'difficulty_display': difficulty_display
        }
        
    def display_generation_summary(self, batch_size: int, max_batches: int, 
                                  ai_provider: str, prompt_params: Dict[str, Any],
                                  dry_run: bool) -> None:
        """Display a summary of what will be generated."""
        self.stdout.write(self.style.SUCCESS(
            f"Generating {batch_size * max_batches} {prompt_params['difficulty_display']} {prompt_params['category_display']} flash cards "
            f"using {ai_provider.upper()} in {max_batches} batch(es)"
        ))
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE: Flash cards will not be added to the database"))
            
    def format_prompt(self, batch_size: int, **kwargs) -> str:
        """Format the AI prompt with given parameters."""
        return AI_PROMPT.format(
            num=batch_size, 
            category_display=kwargs['category_display'],
            category_code=kwargs['category_code'],
            difficulty_display=kwargs['difficulty_display']
        )
    
    def parse_response(self, response: str, batch_size: int) -> List[Dict[str, Any]]:
        """Parse and validate the JSON response from the AI."""
        try:
            # Extract JSON from the response
            json_content = extract_json_from_response(response)
                
            # Parse the JSON
            flash_cards = json.loads(json_content)
            
            # Validate the structure of each flash card
            for card in flash_cards:
                required_fields = ["question", "answer", "feedback", "difficulty", "category"]
                for field in required_fields:
                    if field not in card:
                        raise ValueError(f"Missing required field '{field}' in flash card: {card}")
                        
                # Validate answer is boolean
                if not isinstance(card["answer"], bool):
                    # Try to convert string "true" or "false" to boolean
                    if isinstance(card["answer"], str) and card["answer"].lower() in ["true", "false"]:
                        card["answer"] = card["answer"].lower() == "true"
                    else:
                        raise ValueError(f"Answer must be a boolean value in flash card: {card}")
                        
                if card["difficulty"] not in [code for code, _ in DIFFICULTIES]:
                    raise ValueError(f"Invalid difficulty '{card['difficulty']}' in flash card: {card}")
                    
                if card["category"] not in [code for code, _ in CATEGORIES]:
                    raise ValueError(f"Invalid category '{card['category']}' in flash card: {card}")
            
            # Enforce exact batch size
            if len(flash_cards) > batch_size:
                print(f"Warning: AI generated {len(flash_cards)} flash cards, but only {batch_size} were requested. Truncating to first {batch_size}.")
                flash_cards = flash_cards[:batch_size]
            elif len(flash_cards) < batch_size:
                print(f"Warning: AI generated only {len(flash_cards)} flash cards, but {batch_size} were requested.")
                
            # Check the balance of true/false statements
            true_count = sum(1 for card in flash_cards if card["answer"])
            false_count = len(flash_cards) - true_count
            
            if true_count > 0 and false_count > 0:
                true_percent = (true_count / len(flash_cards)) * 100
                print(f"True/False balance: {true_count} true ({true_percent:.1f}%) / {false_count} false ({100-true_percent:.1f}%)")
            else:
                print(f"Warning: All flash cards are {'true' if true_count else 'false'}. Consider regenerating for better balance.")
                    
            return flash_cards
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}\nResponse: {response[:500]}")
        except Exception as e:
            raise ValueError(f"Error processing response: {str(e)}")
    
    def display_content(self, content_items: List[Dict[str, Any]]) -> None:
        """Display the generated flash cards to the user."""
        for i, card in enumerate(content_items, 1):
            self.stdout.write("\n" + "-" * 40)
            self.stdout.write(self.style.SUCCESS(f"Flash Card {i}:"))
            self.stdout.write(f"Category: {card['category']}")
            self.stdout.write(f"Difficulty: {card['difficulty']}")
            self.stdout.write(f"Statement: {card['question']}")
            self.stdout.write(f"Answer: {'TRUE' if card['answer'] else 'FALSE'}")
            self.stdout.write(f"Feedback: {card['feedback']}")
    
    @transaction.atomic
    def add_to_database(self, content_items: List[Dict[str, Any]]) -> int:
        """
        Add flash cards to the database.
        
        Args:
            content_items: List of flash card dictionaries
            
        Returns:
            Number of flash cards successfully added
        """
        added = 0
        
        for card in content_items:
            try:
                # Check if a similar flash card already exists
                question_text = card['question'].strip()
                
                # 1. Exact match check
                if FlashCard.objects.filter(question=question_text).exists():
                    self.stdout.write(self.style.WARNING(f"Flash card already exists (exact match): {question_text[:50]}..."))
                    continue
                
                # 2. Similarity check - lowercased and stripped of punctuation
                existing_cards = FlashCard.objects.all()
                duplicate_found = False
                
                for existing in existing_cards:
                    if is_similar_text(question_text, existing.question):
                        self.stdout.write(self.style.WARNING(
                            f"Similar flash card already exists:\nNew: {question_text[:50]}...\nExisting: {existing.question[:50]}..."
                        ))
                        duplicate_found = True
                        break
                
                if duplicate_found:
                    continue
                    
                # Create the flash card
                flash_card = FlashCard(
                    question=question_text,
                    answer=card['answer'],
                    feedback=card['feedback'],
                    difficulty=card['difficulty'],
                    category=card['category']
                )
                flash_card.save()
                
                added += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error adding flash card: {str(e)}"))
                
        return added