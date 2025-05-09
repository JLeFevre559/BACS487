"""
Generate multiple choice questions for financial literacy education.
"""
import json
import random
from typing import List, Dict, Any

from django.db import transaction
from ...models import MultipleChoice, MultipleChoiceDistractor, CATEGORIES, DIFFICULTIES
from .base_generation_command import BaseGenerationCommand
from .ai_utils import extract_json_from_response, is_similar_text

# AI prompt template for generating multiple choice questions
AI_PROMPT = """
Generate EXACTLY {num} multiple choice questions about {category_display} for teaching financial literacy. Do not generate more or fewer than {num} questions. Each question should have 1 correct answer and 3 distractors (incorrect answers).

For each question, include:
1. The question text
2. The correct answer
3. Three incorrect answers (distractors)
4. A detailed explanation/feedback on why the correct answer is right
5. Difficulty level (B for Beginner, I for Intermediate, A for Advanced)

Ensure that each question tests understanding, not just recall. Questions should be engaging and relevant for teaching financial concepts.

Return your response as a valid JSON array with EXACTLY {num} objects in this format:
[
  {{
    "question": "Question text here?",
    "answer": "Correct answer here",
    "distractors": ["Incorrect answer 1", "Incorrect answer 2", "Incorrect answer 3"],
    "feedback": "Detailed explanation of why the correct answer is right",
    "difficulty": "Difficulty level here (B, I, A)",
    "category": "{category_code}"
  }}
  {{"json_continuation": "{num}" }}
]

The final JSON array MUST contain EXACTLY {num} question objects, no more and no less.

Only include the valid JSON array in your response, with no additional explanations, preambles, or postscripts.
"""


class Command(BaseGenerationCommand):
    help = 'Generate multiple choice questions using AI and add them to the database'
    content_type_name = "multiple choice questions"
    default_batch_size = 5
    system_message = "You are a financial education expert. Generate multiple choice questions for teaching financial literacy concepts."
    
    def add_model_arguments(self, parser):
        """Add model-specific arguments."""
        parser.add_argument(
            '--category', 
            type=str, 
            choices=[code for code, _ in CATEGORIES],
            help='Category of questions to generate (will use random category if not specified)'
        )
    
    def process_options(self, options: Dict[str, Any], use_random: bool = False) -> Dict[str, Any]:
        """Process command options and return parameters for prompt formatting."""
        from ...models import CATEGORIES
        
        # Use a random category if none was specified or if random was requested
        # Always use random if use_random is True regardless of whether category is specified
        if use_random and ('category' not in options or options['category'] is None):
            # Choose a random category
            category_codes = [code for code, _ in CATEGORIES]
            category = random.choice(category_codes)
            self.stdout.write(self.style.SUCCESS(f"Using randomly selected category: {category}"))
        elif 'category' in options and options['category'] is not None:
            # Use the explicitly specified category
            category = options['category']
        else:
            # No category specified and not forcing random, still use random
            category_codes = [code for code, _ in CATEGORIES]
            category = random.choice(category_codes)
            self.stdout.write(self.style.SUCCESS(f"Using randomly selected category: {category}"))
        
        # Find the display name for the category
        category_display = next((name for code, name in CATEGORIES if code == category), "Budgeting")
        
        return {
            'category_code': category,
            'category_display': category_display
        }
        
    def display_generation_summary(self, batch_size: int, max_batches: int, 
                                  ai_provider: str, prompt_params: Dict[str, Any],
                                  dry_run: bool) -> None:
        """Display a summary of what will be generated."""
        self.stdout.write(self.style.SUCCESS(
            f"Generating {batch_size * max_batches} {prompt_params['category_display']} multiple choice questions "
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
            
            # Remove any metadata objects that might have been added to the JSON array
            questions = [q for q in questions if "json_continuation" not in q]
            
            # Validate the structure of each question
            for q in questions:
                required_fields = ["question", "answer", "distractors", "feedback", "difficulty", "category"]
                for field in required_fields:
                    if field not in q:
                        raise ValueError(f"Missing required field '{field}' in question: {q}")
                        
                if not isinstance(q["distractors"], list):
                    raise ValueError(f"'distractors' must be a list in question: {q}")
                    
                if len(q["distractors"]) != 3:
                    raise ValueError(f"Expected 3 distractors, got {len(q['distractors'])} in question: {q}")
                    
                if q["difficulty"] not in ["B", "I", "A"]:
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
            self.stdout.write(f"Correct Answer: {q['answer']}")
            self.stdout.write("Distractors:")
            for j, d in enumerate(q['distractors'], 1):
                self.stdout.write(f"  {j}. {d}")
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
                if MultipleChoice.objects.filter(question=question_text).exists():
                    self.stdout.write(self.style.WARNING(f"Question already exists (exact match): {question_text[:50]}..."))
                    continue
                
                # 2. Similarity check - lowercased and stripped of punctuation
                existing_questions = MultipleChoice.objects.all()
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
                    
                # Create the multiple choice question
                mc_question = MultipleChoice(
                    question=question_text,
                    answer=q['answer'],
                    feedback=q['feedback'],
                    difficulty=q['difficulty'],
                    category=q['category']
                )
                mc_question.save()
                
                # Create the distractors
                for distractor in q['distractors']:
                    MultipleChoiceDistractor.objects.create(
                        question=mc_question,
                        distractor=distractor
                    )
                    
                added += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error adding question: {str(e)}"))
                
        return added