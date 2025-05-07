"""
Generate match and drag exercises for financial literacy education.
"""
import json
import random
from typing import List, Dict, Any

from django.db import transaction
from ...models import MatchAndDrag, TermsAndDefinitions, CATEGORIES, DIFFICULTIES
from .base_generation_command import BaseGenerationCommand
from .ai_utils import extract_json_from_response, is_similar_text

# AI prompt template for generating match and drag exercises
AI_PROMPT = """
Generate EXACTLY {num} match and drag exercises about {category_display} for teaching financial literacy. Do not generate more or fewer than {num} exercises.

For each exercise, include:
1. A set of 4-6 related financial terms and their definitions
2. A clear, concise feedback explanation about the relationships between these terms
3. Difficulty level (B for Beginner, I for Intermediate, A for Advanced)

Ensure that each match and drag exercise:
- Contains financial terms that are conceptually related
- Has clear, unambiguous definitions that match only one term
- Has terms that are appropriate for the specified difficulty level ({difficulty_display})
- Contains terms specifically relevant to {category_display}

Return your response as a valid JSON array with EXACTLY {num} objects in this format:
[
  {{
    "terms_and_definitions": [
      {{
        "term": "Bond",
        "definition": "A debt investment where an investor loans money to a corporate or government entity for a defined period of time at a fixed interest rate.",
        "feedback": "Bonds are fixed-income instruments that represent loans made by investors to borrowers."
      }},
      {{
        "term": "Stock",
        "definition": "A type of security that represents ownership in a corporation and a claim on part of the corporation's assets and earnings.",
        "feedback": "Stocks give shareholders a share of ownership in a company."
      }},
      ... additional terms and definitions ...
    ],
    "feedback": "These terms represent different types of investment vehicles. Understanding these fundamental investment types is essential for building a diversified portfolio.",
    "difficulty": "Difficulty level here (B, I, A)",
    "category": "{category_code}"
  }},
  ... additional exercises ...
]

The final JSON array MUST contain EXACTLY {num} exercise objects, no more and no less.

Only include the valid JSON array in your response, with no additional explanations, preambles, or postscripts.
"""


class Command(BaseGenerationCommand):
    help = 'Generate match and drag exercises using AI and add them to the database'
    content_type_name = "match and drag exercises"
    default_batch_size = 3
    system_message = "You are a financial education expert. Generate match and drag exercises for teaching financial literacy concepts."
    
    def add_model_arguments(self, parser):
        """Add model-specific arguments."""
        parser.add_argument(
            '--category', 
            type=str, 
            choices=[code for code, _ in CATEGORIES],
            help='Category of exercises to generate (will use random category if not specified)'
        )
        parser.add_argument(
            '--difficulty', 
            type=str, 
            choices=[code for code, _ in DIFFICULTIES],
            default='B',
            help='Difficulty level of exercises to generate'
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
            f"Generating {batch_size * max_batches} {prompt_params['difficulty_display']} {prompt_params['category_display']} match and drag exercises "
            f"using {ai_provider.upper()} in {max_batches} batch(es)"
        ))
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE: Exercises will not be added to the database"))
            
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
            exercises = json.loads(json_content)
            
            # Validate the structure of each exercise
            for exercise in exercises:
                required_fields = ["terms_and_definitions", "feedback", "difficulty", "category"]
                for field in required_fields:
                    if field not in exercise:
                        raise ValueError(f"Missing required field '{field}' in exercise: {exercise}")
                
                # Validate terms and definitions
                if not isinstance(exercise["terms_and_definitions"], list):
                    raise ValueError(f"'terms_and_definitions' must be a list in exercise: {exercise}")
                
                if len(exercise["terms_and_definitions"]) < 4 or len(exercise["terms_and_definitions"]) > 6:
                    raise ValueError(f"Expected 4-6 terms and definitions, got {len(exercise['terms_and_definitions'])} in exercise: {exercise}")
                
                # Validate each term and definition
                for td in exercise["terms_and_definitions"]:
                    td_required = ["term", "definition", "feedback"]
                    for field in td_required:
                        if field not in td:
                            raise ValueError(f"Missing required field '{field}' in term and definition: {td}")
                
                if exercise["difficulty"] not in [code for code, _ in DIFFICULTIES]:
                    raise ValueError(f"Invalid difficulty '{exercise['difficulty']}' in exercise: {exercise}")
                    
                if exercise["category"] not in [code for code, _ in CATEGORIES]:
                    raise ValueError(f"Invalid category '{exercise['category']}' in exercise: {exercise}")
            
            # Enforce exact batch size
            if len(exercises) > batch_size:
                print(f"Warning: AI generated {len(exercises)} exercises, but only {batch_size} were requested. Truncating to first {batch_size}.")
                exercises = exercises[:batch_size]
            elif len(exercises) < batch_size:
                print(f"Warning: AI generated only {len(exercises)} exercises, but {batch_size} were requested.")
                    
            return exercises
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}\nResponse: {response[:500]}")
        except Exception as e:
            raise ValueError(f"Error processing response: {str(e)}")
    
    def display_content(self, content_items: List[Dict[str, Any]]) -> None:
        """Display the generated exercises to the user."""
        for i, exercise in enumerate(content_items, 1):
            self.stdout.write("\n" + "-" * 40)
            self.stdout.write(self.style.SUCCESS(f"Match and Drag Exercise {i}:"))
            self.stdout.write(f"Category: {exercise['category']}")
            self.stdout.write(f"Difficulty: {exercise['difficulty']}")
            self.stdout.write(f"Overall Feedback: {exercise['feedback']}")
            
            self.stdout.write("\nTerms and Definitions:")
            for j, td in enumerate(exercise['terms_and_definitions'], 1):
                self.stdout.write(f"\n  {j}. Term: {td['term']}")
                self.stdout.write(f"     Definition: {td['definition']}")
                self.stdout.write(f"     Feedback: {td['feedback']}")
    
    @transaction.atomic
    def add_to_database(self, content_items: List[Dict[str, Any]]) -> int:
        """
        Add exercises to the database.
        
        Args:
            content_items: List of exercise dictionaries
            
        Returns:
            Number of exercises successfully added
        """
        added = 0
        
        for exercise in content_items:
            try:
                # Check if a similar exercise already exists (based on feedback)
                feedback_text = exercise['feedback'].strip()
                
                # Check for similar feedback to avoid duplicates
                existing_exercises = MatchAndDrag.objects.all()
                duplicate_found = False
                
                for existing in existing_exercises:
                    if is_similar_text(feedback_text, existing.feedback):
                        self.stdout.write(self.style.WARNING(
                            f"Similar exercise already exists:\nNew: {feedback_text[:50]}...\nExisting: {existing.feedback[:50]}..."
                        ))
                        duplicate_found = True
                        break
                
                if duplicate_found:
                    continue
                    
                # Create the match and drag exercise
                match_drag = MatchAndDrag(
                    feedback=feedback_text,
                    difficulty=exercise['difficulty'],
                    category=exercise['category']
                )
                match_drag.save()
                
                # Create the terms and definitions
                for td in exercise['terms_and_definitions']:
                    TermsAndDefinitions.objects.create(
                        question=match_drag,
                        term=td['term'],
                        definition=td['definition'],
                        feedback=td['feedback']
                    )
                    
                added += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error adding exercise: {str(e)}"))
                
        return added