# Generate Flash Cards Command

This Django management command uses AI (OpenAI or Claude) to generate true/false flash cards for financial literacy education and adds them to your database.

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
python manage.py generate_flash_cards
```

By default, this will generate 10 Beginner flash cards about Budgeting using OpenAI, show them to you for approval, and add approved flash cards to the database.

### Options

- `--batch NUMBER`: Number of flash cards to generate in each batch (default: 10)
  ```bash
  python manage.py generate_flash_cards --batch 20
  ```

- `--no-input`: Skip user confirmation for each batch of flash cards
  ```bash
  python manage.py generate_flash_cards --no-input
  ```

- `--max NUMBER`: Maximum number of batches to generate (default: 1)
  ```bash
  python manage.py generate_flash_cards --max 3
  ```

- `--dry-run`: Generate flash cards but do not add them to the database
  ```bash
  python manage.py generate_flash_cards --dry-run
  ```

- `--ai PROVIDER`: AI provider to use for generating flash cards ('openai' or 'claude', default: 'openai')
  ```bash
  python manage.py generate_flash_cards --ai claude
  ```

- `--category CODE`: Category of flash cards to generate (default: 'BUD')
  ```bash
  python manage.py generate_flash_cards --category INV
  ```

- `--difficulty CODE`: Difficulty level of flash cards to generate (default: 'B')
  ```bash
  python manage.py generate_flash_cards --difficulty A
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
1. Display each generated flash card with its statement, true/false answer, and feedback
2. Show statistics on the true/false balance within the batch
3. Ask for your confirmation:
   - Press Enter to accept all flash cards
   - Enter specific numbers to reject (e.g., `1, 3, 5`)
   - Enter `all` to reject all flash cards in the batch

## Examples

Generate 10 Beginner budgeting flash cards using OpenAI:
```bash
python manage.py generate_flash_cards
```

Generate 20 Intermediate flash cards about Investing using Claude without confirmation:
```bash
python manage.py generate_flash_cards --batch 20 --category INV --difficulty I --ai claude --no-input
```

Generate 3 batches of 10 Advanced flash cards about Taxes, with user confirmation:
```bash
python manage.py generate_flash_cards --batch 10 --max 3 --category TAX --difficulty A
```

Test generation without adding to database:
```bash
python manage.py generate_flash_cards --dry-run --ai claude
```

## Output

The command provides detailed output:
- Progress information for each batch
- Statistics on true/false balance within each batch
- Summary of generated and added flash cards
- Warning messages for skipped flash cards (e.g., duplicates)
- Error messages for any issues encountered

## Generated Content

Each generated flash card includes:
- A statement about financial literacy that is either true or false
- A boolean value indicating whether the statement is true or false
- Detailed feedback explaining why the statement is true or false
- Difficulty level (B, I, or A)
- Category code

The flash cards are designed to have a balanced mix of true and false statements (approximately 50% each) and to test understanding of financial concepts rather than simple recall, making them effective for educational purposes.