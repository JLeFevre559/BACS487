"""
Generate budget simulation scenarios for financial literacy education.
"""
import json
import random
from decimal import Decimal, DecimalException
from typing import List, Dict, Any

from django.db import transaction
from django.core.exceptions import ValidationError
from ...models import BudgetSimulation, Expense, CATEGORIES, DIFFICULTIES
from .base_generation_command import BaseGenerationCommand
from .ai_utils import extract_json_from_response, is_similar_text

# AI prompt template for generating budget simulations
AI_PROMPT = """
Generate EXACTLY {num} budget simulation scenarios about {category_display} for teaching financial literacy. Do not generate more or fewer than {num} scenarios. Each scenario should include a monthly income and various expenses that the user needs to categorize as essential or non-essential.

For each budget simulation, include:
1. A scenario description that presents a realistic financial situation related to {category_display}
2. The monthly income amount (as a decimal with 2 decimal places)
3. A list of 5-8 expenses, each with:
   - Name
   - Amount (as a decimal with 2 decimal places)
   - Whether it's essential (true) or non-essential (false)
   - Feedback explaining why the expense is essential or non-essential

Ensure that each scenario:
- Has a realistic monthly income (between $1,500 and $10,000)
- Contains a mix of essential and non-essential expenses
- Has total essential expenses that are less than the monthly income
- Has difficulty level (B for Beginner, I for Intermediate, A for Advanced)
- Includes expenses relevant to {category_display} (e.g., for Credit category, include credit card payments, loan payments, etc.)

Return your response as a valid JSON array with EXACTLY {num} objects in this format:
[
  {{
    "question": "Scenario description here",
    "monthly_income": 3500.00,
    "difficulty": "Difficulty level here (B, I, A)",
    "category": "{category_code}",
    "expenses": [
      {{
        "name": "Rent",
        "amount": 1200.00,
        "essential": true,
        "feedback": "Housing is a basic necessity and is considered an essential expense."
      }},
      {{
        "name": "Streaming Services",
        "amount": 50.00,
        "essential": false,
        "feedback": "Entertainment subscriptions are typically considered non-essential expenses that can be reduced or eliminated if needed."
      }},
      ... additional expenses ...
    ]
  }},
  ... additional scenarios ...
]

The final JSON array MUST contain EXACTLY {num} simulation objects, no more and no less.

Only include the valid JSON array in your response, with no additional explanations, preambles, or postscripts.
"""


class Command(BaseGenerationCommand):
    help = 'Generate budget simulations using AI and add them to the database'
    content_type_name = "budget simulations"
    default_batch_size = 3
    system_message = "You are a financial education expert. Generate budget simulation scenarios for teaching financial literacy concepts."
    
    def add_model_arguments(self, parser):
        """Add model-specific arguments."""
        parser.add_argument(
            '--category', 
            type=str, 
            choices=[code for code, _ in CATEGORIES],
            help='Category of simulations to generate (will use random category if not specified)'
        )
        parser.add_argument(
            '--difficulty', 
            type=str, 
            choices=[code for code, _ in DIFFICULTIES],
            default='B',
            help='Difficulty level of simulations to generate'
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
            f"Generating {batch_size * max_batches} {prompt_params['difficulty_display']} {prompt_params['category_display']} budget simulations "
            f"using {ai_provider.upper()} in {max_batches} batch(es)"
        ))
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE: Simulations will not be added to the database"))
            
    def format_prompt(self, batch_size: int, **kwargs) -> str:
        """Format the AI prompt with given parameters."""
        return AI_PROMPT.format(
            num=batch_size,
            category_code=kwargs['category_code'],
            category_display=kwargs['category_display']
        )
    
    def parse_response(self, response: str, batch_size: int) -> List[Dict[str, Any]]:
        """Parse and validate the JSON response from the AI."""
        try:
            # Extract JSON from the response
            json_content = extract_json_from_response(response)
                
            # Parse the JSON
            simulations = json.loads(json_content)
            
            # Validate the structure of each simulation
            for sim in simulations:
                required_fields = ["question", "monthly_income", "difficulty", "category", "expenses"]
                for field in required_fields:
                    if field not in sim:
                        raise ValueError(f"Missing required field '{field}' in simulation: {sim}")
                        
                if not isinstance(sim["expenses"], list):
                    raise ValueError(f"'expenses' must be a list in simulation: {sim}")
                    
                if len(sim["expenses"]) < 5 or len(sim["expenses"]) > 8:
                    raise ValueError(f"Expected 5-8 expenses, got {len(sim['expenses'])} in simulation: {sim}")
                    
                # Validate monthly income
                try:
                    monthly_income = Decimal(str(sim["monthly_income"]))
                    if monthly_income < 1500 or monthly_income > 10000:
                        raise ValueError(f"Monthly income ${monthly_income} is outside realistic range ($1,500-$10,000)")
                except (ValueError, TypeError, DecimalException):
                    raise ValueError(f"Invalid monthly_income value: {sim['monthly_income']}")
                    
                # Validate expenses
                essential_sum = Decimal('0.00')
                for expense in sim["expenses"]:
                    expense_required = ["name", "amount", "essential", "feedback"]
                    for field in expense_required:
                        if field not in expense:
                            raise ValueError(f"Missing required field '{field}' in expense: {expense}")
                    
                    try:
                        amount = Decimal(str(expense["amount"]))
                        if amount <= 0:
                            raise ValueError(f"Expense amount must be positive: {amount}")
                            
                        if expense["essential"]:
                            essential_sum += amount
                    except (ValueError, TypeError, DecimalException):
                        raise ValueError(f"Invalid amount value: {expense['amount']}")
                
                # Validate that essential expenses don't exceed income
                if essential_sum > monthly_income:
                    raise ValueError(f"Sum of essential expenses (${essential_sum}) exceeds monthly income (${monthly_income})")
                    
                if sim["difficulty"] not in [code for code, _ in DIFFICULTIES]:
                    raise ValueError(f"Invalid difficulty '{sim['difficulty']}' in simulation: {sim}")
                    
                if sim["category"] not in [code for code, _ in CATEGORIES]:
                    raise ValueError(f"Invalid category '{sim['category']}' in simulation: {sim}")
            
            # Enforce exact batch size
            if len(simulations) > batch_size:
                print(f"Warning: AI generated {len(simulations)} simulations, but only {batch_size} were requested. Truncating to first {batch_size}.")
                simulations = simulations[:batch_size]
            elif len(simulations) < batch_size:
                print(f"Warning: AI generated only {len(simulations)} simulations, but {batch_size} were requested.")
                    
            return simulations
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}\nResponse: {response[:500]}")
        except Exception as e:
            raise ValueError(f"Error processing response: {str(e)}")
    
    def display_content(self, content_items: List[Dict[str, Any]]) -> None:
        """Display the generated simulations to the user."""
        for i, sim in enumerate(content_items, 1):
            self.stdout.write("\n" + "-" * 40)
            self.stdout.write(self.style.SUCCESS(f"Simulation {i}:"))
            self.stdout.write(f"Difficulty: {sim['difficulty']}")
            self.stdout.write(f"Category: {sim['category']}")
            self.stdout.write(f"Scenario: {sim['question']}")
            self.stdout.write(f"Monthly Income: ${sim['monthly_income']}")
            
            self.stdout.write("\nExpenses:")
            essential_sum = Decimal('0.00')
            nonessential_sum = Decimal('0.00')
            
            for j, expense in enumerate(sim['expenses'], 1):
                expense_type = "Essential" if expense['essential'] else "Non-essential"
                self.stdout.write(f"  {j}. {expense['name']}: ${expense['amount']} ({expense_type})")
                self.stdout.write(f"     Feedback: {expense['feedback']}")
                
                # Calculate sums
                amount = Decimal(str(expense['amount']))
                if expense['essential']:
                    essential_sum += amount
                else:
                    nonessential_sum += amount
            
            total_sum = essential_sum + nonessential_sum
            self.stdout.write(f"\nSummary:")
            self.stdout.write(f"  Essential Expenses: ${essential_sum:.2f} ({(essential_sum/Decimal(str(sim['monthly_income']))*100):.1f}% of income)")
            self.stdout.write(f"  Non-essential Expenses: ${nonessential_sum:.2f} ({(nonessential_sum/Decimal(str(sim['monthly_income']))*100):.1f}% of income)")
            self.stdout.write(f"  Total Expenses: ${total_sum:.2f} ({(total_sum/Decimal(str(sim['monthly_income']))*100):.1f}% of income)")
            self.stdout.write(f"  Remaining: ${Decimal(str(sim['monthly_income'])) - total_sum:.2f} ({(1-(total_sum/Decimal(str(sim['monthly_income']))))*100:.1f}% of income)")
    
    @transaction.atomic
    def add_to_database(self, content_items: List[Dict[str, Any]]) -> int:
        """
        Add simulations to the database.
        
        Args:
            content_items: List of simulation dictionaries
            
        Returns:
            Number of simulations successfully added
        """
        added = 0
        
        for sim in content_items:
            try:
                # Check if a similar simulation already exists
                question_text = sim['question'].strip()
                
                # 1. Exact match check
                if BudgetSimulation.objects.filter(question=question_text).exists():
                    self.stdout.write(self.style.WARNING(f"Simulation already exists (exact match): {question_text[:50]}..."))
                    continue
                
                # 2. Similarity check - lowercased and stripped of punctuation
                existing_simulations = BudgetSimulation.objects.all()
                duplicate_found = False
                
                for existing in existing_simulations:
                    if is_similar_text(question_text, existing.question):
                        self.stdout.write(self.style.WARNING(
                            f"Similar simulation already exists:\nNew: {question_text[:50]}...\nExisting: {existing.question[:50]}..."
                        ))
                        duplicate_found = True
                        break
                
                if duplicate_found:
                    continue
                    
                # Create the budget simulation
                budget_sim = BudgetSimulation(
                    question=question_text,
                    monthly_income=Decimal(str(sim['monthly_income'])),
                    difficulty=sim['difficulty'],
                    category=sim['category']
                )
                budget_sim.save()
                
                # Create the expenses
                for expense_data in sim['expenses']:
                    Expense.objects.create(
                        BudgetSimulation=budget_sim,
                        name=expense_data['name'],
                        amount=Decimal(str(expense_data['amount'])),
                        feedback=expense_data['feedback'],
                        essential=expense_data['essential']
                    )
                    
                added += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error adding simulation: {str(e)}"))
                
        return added