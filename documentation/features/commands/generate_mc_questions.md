# Generate Multiple Choice Questions Command

This Django management command uses AI (OpenAI or Claude) to generate multiple choice questions for financial literacy education and adds them to your database.

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
python manage.py generate_mc_questions
```

By default, this will generate 5 questions about Budgeting using OpenAI, show them to you for approval, and add approved questions to the database.

### Options

- `--batch NUMBER`: Number of questions to generate in each batch (default: 5)
  ```bash
  python manage.py generate_mc_questions --batch 10
  ```

- `--no-input`: Skip user confirmation for each batch of questions
  ```bash
  python manage.py generate_mc_questions --no-input
  ```

- `--max NUMBER`: Maximum number of batches to generate (default: 1)
  ```bash
  python manage.py generate_mc_questions --max 3
  ```

- `--dry-run`: Generate questions but do not add them to the database
  ```bash
  python manage.py generate_mc_questions --dry-run
  ```

- `--ai PROVIDER`: AI provider to use for generating questions ('openai' or 'claude', default: 'openai')
  ```bash
  python manage.py generate_mc_questions --ai claude
  ```

- `--category CODE`: Category of questions to generate (default: 'BUD')
  ```bash
  python manage.py generate_mc_questions --category INV
  ```

### Available Categories

- `BUD`: Budgeting
- `INV`: Investing
- `SAV`: Savings
- `BAL`: Balance Sheet
- `CRD`: Credit
- `TAX`: Taxes

## Interactive Mode

When not using `--no-input`, the command will:
1. Display each generated question with its correct answer, distractors, and feedback
2. Ask for your confirmation:
   - Press Enter to accept all questions
   - Enter specific numbers to reject (e.g., `1, 3, 5`)
   - Enter `all` to reject all questions in the batch

## Examples

Generate 5 Beginner budgeting questions using OpenAI:
```bash
python manage.py generate_mc_questions
```

Generate 10 questions about Investing using Claude without confirmation:
```bash
python manage.py generate_mc_questions --batch 10 --category INV --ai claude --no-input
```

Generate 3 batches of 5 questions each about Credit, with user confirmation:
```bash
python manage.py generate_mc_questions --batch 5 --max 3 --category CRD
```

Test generation without adding to database:
```bash
python manage.py generate_mc_questions --dry-run --ai claude
```

## Output

The command provides detailed output:
- Progress information for each batch
- Summary of generated and added questions
- Warning messages for skipped questions (e.g., duplicates)
- Error messages for any issues encountered

## Generated Content

Each generated question includes:
- Question text
- Correct answer
- Three incorrect answers (distractors)
- Detailed feedback explaining the correct answer
- Difficulty level (B, I, or A)
- Category code

The questions are designed to test understanding of financial concepts rather than simple recall, making them effective for educational purposes.