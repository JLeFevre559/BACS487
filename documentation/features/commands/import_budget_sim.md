# Budget Simulation Import Command

This Django management command allows you to import budget simulations from a JSON file into the database.

## Usage

Run the command using Django's `manage.py`:

```bash
python manage.py import_budget_simulations path/to/your/simulations.json
```

### Options

- `--dry-run`: Validate the JSON file without saving to the database
  ```bash
  python manage.py import_budget_simulations path/to/your/simulations.json --dry-run
  ```

## JSON Format

The JSON file should contain an array of budget simulation objects, each with the following structure:

```json
[
  {
    "question": "Text of the budget simulation question",
    "monthly_income": 3500.00,
    "difficulty": "B",  // B for Beginner, I for Intermediate, A for Advanced
    "category": "BUD",  // Optional: defaults to "BUD" if not specified
    "expenses": [
      {
        "name": "Expense name",
        "amount": 1200.00,
        "feedback": "Educational feedback about this expense",
        "essential": true  // Whether this is an essential expense
      },
      // More expenses...
    ]
  },
  // More simulations...
]
```

### Fields

- `question` (required): The text prompt for the budget simulation
- `monthly_income` (required): The monthly income amount for the simulation
- `difficulty` (required): The difficulty level of the simulation 
  - `B`: Beginner
  - `I`: Intermediate
  - `A`: Advanced
- `category` (optional): The financial category for the simulation
  - `BUD`: Budgeting (default)
  - `INV`: Investing
  - `SAV`: Savings
  - `BAL`: Balance Sheet
  - `CRD`: Credit
  - `TAX`: Taxes
- `expenses` (required): An array of expense objects, each containing:
  - `name` (required): The name of the expense
  - `amount` (required): The dollar amount of the expense
  - `feedback` (required): Educational feedback about this expense
  - `essential` (optional): Whether this expense is essential (defaults to false)

## Validation

The command performs the following validations:

1. The JSON file format is valid
2. Required fields are present for each simulation
3. The difficulty value is valid (B, I, or A)
4. The category value is valid (BUD, INV, SAV, BAL, CRD, TAX)
5. The sum of essential expenses does not exceed the monthly income
6. Each expense has required fields
7. No duplicate questions exist in the database

If any validation fails, the command will not import that simulation and will report the error.

## Example

```bash
# Validate the file without importing
python manage.py import_budget_simulations sample_budget_simulations.json --dry-run

# Import the simulations to the database
python manage.py import_budget_simulations sample_budget_simulations.json
```

## Sample JSON

Here's an example of a valid JSON file with two budget simulations:

```json
[
  {
    "question": "Create a monthly budget for a college student with a part-time job",
    "monthly_income": 1500.00,
    "difficulty": "B",
    "category": "BUD",
    "expenses": [
      {
        "name": "Rent",
        "amount": 650.00,
        "feedback": "Housing is typically the largest expense in a student budget",
        "essential": true
      },
      {
        "name": "Groceries",
        "amount": 250.00,
        "feedback": "Meal planning can help reduce food costs",
        "essential": true
      },
      {
        "name": "Textbooks",
        "amount": 150.00,
        "feedback": "Consider buying used textbooks or renting to save money",
        "essential": true
      },
      {
        "name": "Entertainment",
        "amount": 100.00,
        "feedback": "Look for student discounts on entertainment options",
        "essential": false
      }
    ]
  },
  {
    "question": "Plan a retirement savings strategy for a 35-year-old professional",
    "monthly_income": 6000.00,
    "difficulty": "I",
    "category": "SAV",
    "expenses": [
      {
        "name": "401(k) Contribution",
        "amount": 900.00,
        "feedback": "Contributing at least 15% of income to retirement is recommended",
        "essential": true
      },
      {
        "name": "Roth IRA Contribution",
        "amount": 500.00,
        "feedback": "A Roth IRA offers tax-free growth and withdrawals in retirement",
        "essential": false
      },
      {
        "name": "Emergency Fund Contribution",
        "amount": 300.00,
        "feedback": "Aim to save 3-6 months of expenses in an emergency fund",
        "essential": true
      }
    ]
  }
]
```