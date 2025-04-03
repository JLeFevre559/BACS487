import json
import os
import time
from decimal import Decimal
from typing import List, Dict, Any, Optional

import anthropic
import openai
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ValidationError
from dotenv import load_dotenv

from ...models import MultipleChoice, MultipleChoiceDistractor, CATEGORIES

# Load environment variables
load_dotenv()

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
    "difficulty": "B",
    "category": "{category_code}"
  }}
  {{"json_continuation": "{num}" }}
]

The final JSON array MUST contain EXACTLY {num} question objects, no more and no less.

Only include the valid JSON array in your response, with no additional explanations, preambles, or postscripts.
"""


def get_openai_response(prompt: str) -> str:
    """
    Get a response from OpenAI API.
    
    Args:
        prompt: The prompt to send to OpenAI
        
    Returns:
        The text response from OpenAI
    """
    # Set up the OpenAI API key
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Less expensive model
            messages=[
                {"role": "system", "content": "You are a financial education expert. Generate multiple choice questions for teaching financial literacy concepts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2048,  # Cap the token usage
        )
        return response.choices[0].message.content
    except Exception as e:
        raise CommandError(f"Error calling OpenAI API: {str(e)}")


def get_claude_response(prompt: str) -> str:
    """
    Get a response from Anthropic Claude API.
    
    Args:
        prompt: The prompt to send to Claude
        
    Returns:
        The text response from Claude
    """
    # Set up the Claude API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-3-haiku-20240307",  # Less expensive model
            max_tokens=1000,  # Cap the token usage
            system="You are a financial education expert. Generate multiple choice questions for teaching financial literacy concepts.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    except Exception as e:
        raise CommandError(f"Error calling Claude API: {str(e)}")


def parse_json_response(response: str, batch_size: int) -> List[Dict[str, Any]]:
    """
    Parse the JSON response from the AI.
    
    Args:
        response: The text response from the AI
        batch_size: The expected number of questions
        
    Returns:
        A list of question dictionaries
    """
    # Extract JSON from the response
    try:
        # Find JSON content (which may be wrapped in markdown code blocks)
        json_content = response
        
        # If the response includes code blocks, extract the JSON
        if "```json" in response:
            json_content = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_content = response.split("```")[1].split("```")[0].strip()
            
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


class Command(BaseCommand):
    help = 'Generate multiple choice questions using AI and add them to the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch', 
            type=int, 
            default=5,
            help='Number of questions to generate in each batch'
        )
        parser.add_argument(
            '--no-input', 
            action='store_true',
            help='Skip user confirmation for each batch'
        )
        parser.add_argument(
            '--max', 
            type=int, 
            default=1,
            help='Maximum number of batches to generate'
        )
        parser.add_argument(
            '--dry-run', 
            action='store_true',
            help='Generate questions but do not add them to the database'
        )
        parser.add_argument(
            '--ai', 
            type=str, 
            choices=['openai', 'claude'],
            default='openai',
            help='AI provider to use for generating questions'
        )
        parser.add_argument(
            '--category', 
            type=str, 
            choices=[code for code, _ in CATEGORIES],
            default='BUD',
            help='Category of questions to generate'
        )

    def handle(self, *args, **options):
        batch_size = options['batch']
        no_input = options['no_input']
        max_batches = options['max']
        dry_run = options['dry_run']
        ai_provider = options['ai']
        category = options['category']
        
        # Find the display name for the category
        category_display = next((name for code, name in CATEGORIES if code == category), "Budgeting")
        
        self.stdout.write(self.style.SUCCESS(
            f"Generating {batch_size * max_batches} {category_display} questions "
            f"using {ai_provider.upper()} in {max_batches} batch(es)"
        ))
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE: Questions will not be added to the database"))
            
        total_added = 0
        total_generated = 0
        
        for batch in range(1, max_batches + 1):
            self.stdout.write("-" * 50)
            self.stdout.write(self.style.SUCCESS(f"Generating batch {batch}/{max_batches}..."))
            
            # Format the prompt with the current batch information
            prompt = AI_PROMPT.format(
                num=batch_size, 
                category_display=category_display,
                category_code=category
            )
            
            # Get response from selected AI provider
            try:
                if ai_provider == 'openai':
                    response = get_openai_response(prompt)
                else:  # claude
                    response = get_claude_response(prompt)
                    
                # Parse the response with the expected batch size
                questions = parse_json_response(response, batch_size)
                total_generated += len(questions)
                
                self.stdout.write(self.style.SUCCESS(f"Generated {len(questions)} questions"))
                
                # Output questions and get user confirmation if needed
                if not no_input:
                    self.display_questions(questions)
                    rejected_indices = self.get_user_confirmation()
                    
                    if rejected_indices == "all":
                        self.stdout.write(self.style.WARNING("Rejected all questions in this batch"))
                        continue
                    
                    # Remove rejected questions
                    questions = [q for i, q in enumerate(questions, 1) if i not in rejected_indices]
                    
                # Add questions to database
                if not dry_run:
                    added = self.add_to_database(questions)
                    total_added += added
                    self.stdout.write(self.style.SUCCESS(f"Added {added} questions to the database"))
                else:
                    self.stdout.write(self.style.WARNING("DRY RUN: Questions not added to database"))
                    
                # Add a small delay between batches to respect API rate limits
                if batch < max_batches:
                    time.sleep(2)
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error in batch {batch}: {str(e)}"))
                continue
                
        # Output final summary
        self.stdout.write("=" * 50)
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"Dry run complete. Generated {total_generated} questions."))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Generation complete. Added {total_added}/{total_generated} questions to the database."
                )
            )

    def display_questions(self, questions: List[Dict[str, Any]]) -> None:
        """Display the generated questions to the user."""
        for i, q in enumerate(questions, 1):
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
            
    def get_user_confirmation(self) -> List[int]:
        """
        Get user confirmation for the batch of questions.
        
        Returns:
            List of indices to reject, or "all" to reject all
        """
        while True:
            self.stdout.write("\nEnter question numbers to reject (e.g., '1, 3, 5'), 'all' to reject all, or press Enter to accept all: ")
            user_input = input().strip().lower()
            
            if not user_input:
                return []  # Accept all
                
            if user_input == 'all':
                return "all"  # Reject all
                
            try:
                # Parse the input as a list of numbers
                rejected = []
                for part in user_input.split(','):
                    # Handle formats like "1" or "reject 1"
                    num_str = part.strip().replace('reject', '').strip()
                    if num_str:
                        rejected.append(int(num_str))
                return rejected
            except ValueError:
                self.stdout.write(self.style.ERROR("Invalid input. Please enter numbers separated by commas."))
    
    @transaction.atomic
    def add_to_database(self, questions: List[Dict[str, Any]]) -> int:
        """
        Add questions to the database.
        
        Args:
            questions: List of question dictionaries
            
        Returns:
            Number of questions successfully added
        """
        added = 0
        
        for q in questions:
            try:
                # Check if a similar question already exists - more thorough check
                question_text = q['question'].strip()
                
                # 1. Exact match check
                if MultipleChoice.objects.filter(question=question_text).exists():
                    self.stdout.write(self.style.WARNING(f"Question already exists (exact match): {question_text[:50]}..."))
                    continue
                
                # 2. Similarity check - lowercased and stripped of punctuation
                simplified_text = ''.join(c.lower() for c in question_text if c.isalnum() or c.isspace()).strip()
                
                existing_questions = MultipleChoice.objects.all()
                for existing in existing_questions:
                    existing_simplified = ''.join(c.lower() for c in existing.question if c.isalnum() or c.isspace()).strip()
                    
                    # If the simplified texts are very similar, consider it a duplicate
                    if simplified_text == existing_simplified or (
                        len(simplified_text) > 20 and  # Only for longer questions
                        (simplified_text in existing_simplified or existing_simplified in simplified_text)
                    ):
                        self.stdout.write(self.style.WARNING(
                            f"Similar question already exists:\nNew: {question_text[:50]}...\nExisting: {existing.question[:50]}..."
                        ))
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