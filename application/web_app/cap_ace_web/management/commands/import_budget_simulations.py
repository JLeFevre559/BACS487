import json
import os
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ValidationError
from ...models import BudgetSimulation, Expense


class Command(BaseCommand):
    help = 'Import budget simulations from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file containing budget simulations')
        parser.add_argument('--dry-run', action='store_true', help='Validate without saving to database')

    def handle(self, *args, **options):
        json_file_path = options['json_file']
        dry_run = options['dry_run']

        if not os.path.exists(json_file_path):
            raise CommandError(f'File {json_file_path} does not exist')

        try:
            with open(json_file_path, 'r') as file:
                data = json.load(file)
        except json.JSONDecodeError:
            raise CommandError(f'Invalid JSON format in {json_file_path}')

        if not isinstance(data, list):
            raise CommandError('JSON file must contain a list of budget simulations')

        successful_imports = 0
        errors = []

        for index, simulation_data in enumerate(data, 1):
            try:
                with transaction.atomic():
                    # Extract simulation data
                    question = simulation_data.get('question')
                    monthly_income = simulation_data.get('monthly_income')
                    difficulty = simulation_data.get('difficulty')
                    expenses = simulation_data.get('expenses', [])

                    # Validate required fields
                    if not question:
                        raise ValidationError(f'Simulation {index}: Question is required')
                    if not monthly_income:
                        raise ValidationError(f'Simulation {index}: Monthly income is required')
                    if difficulty not in ['B', 'I', 'A']:
                        raise ValidationError(f'Simulation {index}: Difficulty must be B, I, or A')
                    if not expenses:
                        raise ValidationError(f'Simulation {index}: At least one expense is required')

                    # Create simulation
                    simulation = BudgetSimulation(
                        question=question,
                        monthly_income=Decimal(str(monthly_income)),
                        difficulty=difficulty
                    )

                    # Check that a question with the same text doesn't already exist
                    if BudgetSimulation.objects.filter(question=question).exists():
                        raise ValidationError(f'Simulation {index}: Question already exists')

                    # Check if this is just a validation run
                    if dry_run:
                        # Don't save, just validate
                        simulation.clean()
                        
                        # Validate expenses
                        essential_sum = Decimal('0')
                        for expense_data in expenses:
                            if expense_data.get('essential', False):
                                essential_sum += Decimal(str(expense_data.get('amount', 0)))
                                
                        if essential_sum > Decimal(str(monthly_income)):
                            raise ValidationError(
                                f'Simulation {index}: Sum of essential expenses (${essential_sum}) '
                                f'exceeds monthly income (${monthly_income})'
                            )
                    else:
                        # Save the simulation
                        simulation.save()

                        # Create expenses
                        for expense_data in expenses:
                            expense = Expense(
                                BudgetSimulation=simulation,
                                name=expense_data.get('name', ''),
                                amount=Decimal(str(expense_data.get('amount', 0))),
                                feedback=expense_data.get('feedback', ''),
                                essential=expense_data.get('essential', False)
                            )
                            expense.save()

                        # Validate the simulation with its expenses
                        simulation.clean()

                    successful_imports += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'Successfully validated simulation {index}' if dry_run else
                        f'Successfully imported simulation {index}'
                    ))

            except ValidationError as e:
                errors.append(f'Simulation {index}: {str(e)}')
            except Exception as e:
                errors.append(f'Simulation {index}: Unexpected error - {str(e)}')
                
        # Output summary
        self.stdout.write('-' * 50)
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'Validated {successful_imports} of {len(data)} simulations'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Imported {successful_imports} of {len(data)} simulations'))
            
        if errors:
            self.stdout.write(self.style.ERROR('The following errors occurred:'))
            for error in errors:
                self.stdout.write(self.style.ERROR(f'  - {error}'))
            return

        if successful_imports == len(data):
            self.stdout.write(self.style.SUCCESS('All simulations processed successfully!'))