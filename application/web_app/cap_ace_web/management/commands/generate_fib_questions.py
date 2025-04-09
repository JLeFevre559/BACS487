"""
Generate fill-in-the-blank questions for financial literacy education.
"""
import json
import random
from typing import List, Dict, Any

from django.db import transaction
from ...models import FillInTheBlank, CATEGORIES, DIFFICULTIES
from .base_generation_command import BaseGenerationCommand
from .ai_utils import extract_json_from_response, is_similar_text

# AI prompt template for generating fill in the blank questions
AI_PROMPT = """
Generate EXACTLY {num} fill-in-the-blank questions about {category_display} for teaching financial literacy. Do not generate more or fewer than {num} questions.

For each question, include:
1. The complete question text with the blank indicated by "___"
2. The missing word or phrase that should fill the blank
3. A detailed explanation/feedback on why this answer is correct
4. Difficulty level (B for Beginner, I for Intermediate, A for Advanced)

Ensure that each question:
- Tests understanding, not just recall
- Has a single, unambiguous missing word or short phrase (1-3 words maximum)
- Is clear and grammatically correct
- Has a missing word that is significant to the meaning (not just an article or minor word)

Return your response as a valid JSON array with EXACTLY {num} objects in this format:
[
  {{
    "question": "A financial plan that tracks income and expenses is called a ___.",
    "answer": "budget",
    "missing_word": "budget",
    "feedback": "A budget is a financial plan that helps individuals track and manage their income and expenses. It's a fundamental tool for financial planning and management.",
    "difficulty": "Difficulty level here (B, I, A)",
    "category": "{category_code}"
  }},
  ... additional questions ...
]

The final JSON array MUST contain EXACTLY {num} question objects, no more and no less.

Only include the valid JSON array in your response, with no additional explanations, preambles, or postscripts.
"""


class Command(BaseGenerationCommand):
    help = 'Generate fill-in-the-blank questions using AI and add them to the database'
    content_type_name = "fill-in-the-blank questions"
    default_batch_size = 5
    system_message = "You are a financial education expert. Generate fill-in-the-blank questions for teaching financial literacy concepts."
    
    def add_model_arguments(self, parser):
        """Add model-specific arguments."""
        parser.add_argument(
            '--category', 
            type=str, 
            choices=[code for code, _ in CATEGORIES],
            help='Category of questions to generate (will use random category if not specified)'
        )
        parser.add_argument(
            '--difficulty', 
            type=str, 
            choices=[code for code, _ in DIFFICULTIES],
            default='B',
            help='Difficulty level of questions to generate'
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
            f"Generating {batch_size * max_batches} {prompt_params['difficulty_display']} {prompt_params['category_display']} fill-in-the-blank questions "
            f"using {ai_provider.upper()} in {max_batches} batch(es)"
        ))
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE: Questions will not be added to the database"))
            
    def format_prompt(self, batch_size: int, **kwargs) -> str:
        """Format the AI prompt with given parameters."""
        return AI_PROMPT.format(
            num=batch_size, 
            category_display=kwargs['category_display'],
            category_code=kwargs['category_code']
        )
    
    def parse_response(self, response: str, batch_size: int) -> List[Dict[str, Any]]:
        """Parse and validate the JSON response from the AI."""
        try:
            # Extract JSON from the response
            json_content = extract_json_from_response(response)
                
            # Parse the JSON
            questions = json.loads(json_content)
            
            # Validate the structure of each question
            for q in questions:
                required_fields = ["question", "answer", "missing_word", "feedback", "difficulty", "category"]
                for field in required_fields:
                    if field not in q:
                        raise ValueError(f"Missing required field '{field}' in question: {q}")
                        
                # Validate question has a blank
                if "___" not in q["question"]:
                    raise ValueError(f"Question does not contain a blank (___): {q['question']}")
                    
                # Validate missing_word matches answer
                if q["missing_word"] != q["answer"]:
                    print(f"Warning: 'missing_word' ({q['missing_word']}) doesn't match 'answer' ({q['answer']}). Using 'answer' as the correct value.")
                    q["missing_word"] = q["answer"]
                    
                # Validate missing_word is not too long
                words = q["missing_word"].split()
                if len(words) > 3:
                    raise ValueError(f"Missing word/phrase '{q['missing_word']}' is too long (more than 3 words)")
                    
                if q["difficulty"] not in [code for code, _ in DIFFICULTIES]:
                    raise ValueError(f"Invalid difficulty '{q['difficulty']}' in question: {q}")
                    
                if q["category"] not in [code for code, _ in CATEGORIES]:
                    raise ValueError(f"Invalid category '{q['category']}' in question: {q}")
            
            # Enforce exact batch size
            if len(questions) > batch_size:
                print(f"Warning: AI generated {len(questions)} questions, but only {batch_size} were requested. Truncating to first {batch_size}.")
                questions = questions[:batch_size]
            elif len(questions) < batch_size:
                print(f"Warning: AI generated only {len(questions)} questions, but {batch_size} were requested.")
                    
            return questions
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}\nResponse: {response[:500]}")
        except Exception as e:
            raise ValueError(f"Error processing response: {str(e)}")
    
    def display_content(self, content_items: List[Dict[str, Any]]) -> None:
        """Display the generated questions to the user."""
        for i, q in enumerate(content_items, 1):
            self.stdout.write("\n" + "-" * 40)
            self.stdout.write(self.style.SUCCESS(f"Question {i}:"))
            self.stdout.write(f"Category: {q['category']}")
            self.stdout.write(f"Difficulty: {q['difficulty']}")
            self.stdout.write(f"Question: {q['question']}")
            self.stdout.write(f"Answer: {q['answer']}")
            self.stdout.write(f"Missing Word: {q['missing_word']}")
            self.stdout.write(f"Feedback: {q['feedback']}")
    
    @transaction.atomic
    def add_to_database(self, content_items: List[Dict[str, Any]]) -> int:
        """
        Add questions to the database.
        
        Args:
            content_items: List of question dictionaries
            
        Returns:
            Number of questions successfully added
        """
        added = 0
        
        for q in content_items:
            try:
                # Check if a similar question already exists
                question_text = q['question'].strip()
                
                # 1. Exact match check
                if FillInTheBlank.objects.filter(question=question_text).exists():
                    self.stdout.write(self.style.WARNING(f"Question already exists (exact match): {question_text[:50]}..."))
                    continue
                
                # 2. Similarity check - lowercased and stripped of punctuation
                existing_questions = FillInTheBlank.objects.all()
                duplicate_found = False
                
                for existing in existing_questions:
                    if is_similar_text(question_text, existing.question):
                        self.stdout.write(self.style.WARNING(
                            f"Similar question already exists:\nNew: {question_text[:50]}...\nExisting: {existing.question[:50]}..."
                        ))
                        duplicate_found = True
                        break
                
                if duplicate_found:
                    continue
                    
                # Create the fill-in-the-blank question
                fib_question = FillInTheBlank(
                    question=question_text,
                    answer=q['answer'],
                    missing_word=q['missing_word'],
                    feedback=q['feedback'],
                    difficulty=q['difficulty'],
                    category=q['category']
                )
                fib_question.save()
                
                added += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error adding question: {str(e)}"))
                
        return added