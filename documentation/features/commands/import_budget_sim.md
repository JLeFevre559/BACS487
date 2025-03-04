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

## Validation

The command performs the following validations:

1. The JSON file format is valid
2. Required fields are present for each simulation
3. The sum of essential expenses does not exceed the monthly income
4. Each expense has required fields

If any validation fails, the command will not import that simulation and will report the error.

## Example

```bash
# Validate the file without importing
python manage.py import_budget_simulations sample_budget_simulations.json --dry-run

# Import the simulations to the database
python manage.py import_budget_simulations sample_budget_simulations.json
```

## Sample JSON

A sample JSON file `sample_budget_simulations.json` is provided with two example budget simulations.