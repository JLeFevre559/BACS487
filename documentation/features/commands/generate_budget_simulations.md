# Generate Budget Simulations Command

This Django management command uses AI (OpenAI or Claude) to generate budget simulation scenarios for financial literacy education and adds them to your database.

## Setup

Before using this command, you need to set up your API keys:

1. Create a `.env` file in your project root with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_claude_api_key_here
   ```

2. Install required packages:
   ```bash
   pip install python-dotenv openai anthropic
   ```

## Usage

Run the command using Django's `manage.py`:

```bash
python manage.py generate_budget_simulations
```

By default, this will generate 3 Beginner budget simulations about Budgeting using OpenAI, show them to you for approval, and add approved simulations to the database.

### Options

- `--batch NUMBER`: Number of simulations to generate in each batch (default: 3)
  ```bash
  python manage.py generate_budget_simulations --batch 5
  ```

- `--no-input`: Skip user confirmation for each batch of simulations
  ```bash
  python manage.py generate_budget_simulations --no-input
  ```

- `--max NUMBER`: Maximum number of batches to generate (default: 1)
  ```bash
  python manage.py generate_budget_simulations --max 3
  ```

- `--dry-run`: Generate simulations but do not add them to the database
  ```bash
  python manage.py generate_budget_simulations --dry-run
  ```

- `--ai PROVIDER`: AI provider to use for generating simulations ('openai' or 'claude', default: 'openai')
  ```bash
  python manage.py generate_budget_simulations --ai claude
  ```

- `--category CODE`: Category of simulations to generate (default: 'BUD')
  ```bash
  python manage.py generate_budget_simulations --category CRD
  ```

- `--difficulty CODE`: Difficulty level of simulations to generate (default: 'B')
  ```bash
  python manage.py generate_budget_simulations --difficulty I
  ```

### Available Categories

- `BUD`: Budgeting
- `INV`: Investing
- `SAV`: Savings
- `BAL`: Balance Sheet
- `CRD`: Credit
- `TAX`: Taxes

### Available Difficulties

- `B`: Beginner
- `I`: Intermediate
- `A`: Advanced

## Interactive Mode

When not using `--no-input`, the command will:
1. Display each generated simulation with its monthly income, expenses (essential and non-essential), and feedback
2. Show a summary of essential vs. non-essential expenses and percentage of income
3. Ask for your confirmation:
   - Press Enter to accept all simulations
   - Enter specific numbers to reject (e.g., `1, 3`)
   - Enter `all` to reject all simulations in the batch

## Examples

Generate 3 Beginner budget simulations about Budgeting using OpenAI:
```bash
python manage.py generate_budget_simulations
```

Generate 5 Intermediate budget simulations about Credit using Claude without confirmation:
```bash
python manage.py generate_budget_simulations --batch 5 --category CRD --difficulty I --ai claude --no-input
```

Generate 3 batches of 3 simulations each about Investing at Advanced difficulty, with user confirmation:
```bash
python manage.py generate_budget_simulations --batch 3 --max 3 --category INV --difficulty A
```

Test generation without adding to database:
```bash
python manage.py generate_budget_simulations --dry-run --category TAX --ai claude
```

## Output

The command provides detailed output:
- Progress information for each batch
- Summary of generated and added simulations
- Warning messages for skipped simulations (e.g., duplicates)
- Error messages for any issues encountered

## Generated Content

Each generated budget simulation includes:
- Scenario description (question)
- Monthly income amount
- 5-8 expenses, each with:
  - Name
  - Amount
  - Essential/non-essential status
  - Feedback explaining why it's essential or non-essential
- Difficulty level (B, I, or A)
- Category code

The simulations are designed to create realistic financial scenarios with appropriate income levels and a mix of essential and non-essential expenses, ensuring that essential expenses don't exceed the monthly income. Each simulation will include expenses specifically relevant to the selected category (e.g., credit card payments for Credit category, investment options for Investing category).