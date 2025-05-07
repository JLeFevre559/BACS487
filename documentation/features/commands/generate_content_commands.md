# Financial Literacy Content Generation Commands

This document provides an overview of the Django management commands available for generating educational content for your financial literacy application.

## Overview

These commands use AI (OpenAI or Claude) to generate various types of educational content and add them to your database. Each command is specialized for a specific content type:

1. **Multiple Choice Questions** (`generate_mc_questions.py`)
2. **Fill-in-the-Blank Questions** (`generate_fib_questions.py`)
3. **True/False Flash Cards** (`generate_flash_cards.py`)
4. **Budget Simulations** (`generate_budget_simulations.py`)
5. **Match and Drag Exercises** (`generate_match_drag.py`)

## Common Setup

Before using any of these commands, you need to set up your API keys:

1. Create a `.env` file in your project root with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_claude_api_key_here
   ```

2. Install required packages:
   ```bash
   pip install python-dotenv openai anthropic
   ```

## Common Options

All five commands share these common options:

- `--batch NUMBER`: Number of items to generate in each batch (default varies by command)
- `--no-input`: Skip user confirmation for each batch
- `--max NUMBER`: Maximum number of batches to generate (default: 1)
- `--dry-run`: Generate content but do not add it to the database
- `--ai PROVIDER`: AI provider to use ('openai' or 'claude', default: 'openai')
- `--category CODE`: Category of content to generate (if not specified, a random category will be used for each batch)
- `--difficulty CODE`: Difficulty level to generate (default: 'B')

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

## Command-Specific Information

### 1. Multiple Choice Questions

Generates questions with one correct answer and three incorrect distractors.

**Usage:**
```bash
python manage.py generate_mc_questions
```

**Default batch size:** 5 questions

**Example:**
```bash
python manage.py generate_mc_questions --batch 10 --category INV --ai claude
```

### 2. Fill-in-the-Blank Questions

Generates questions with a blank (indicated by "___") that students need to fill in.

**Usage:**
```bash
python manage.py generate_fib_questions
```

**Default batch size:** 5 questions

**Example:**
```bash
python manage.py generate_fib_questions --batch 10 --category CRD --difficulty I
```

### 3. True/False Flash Cards

Generates statements that are either true or false about financial concepts.

**Usage:**
```bash
python manage.py generate_flash_cards
```

**Default batch size:** 10 flash cards

**Example:**
```bash
python manage.py generate_flash_cards --batch 20 --category TAX --difficulty A
```

### 4. Budget Simulations

Generates financial scenarios with monthly income and expenses that need to be categorized as essential or non-essential.

**Usage:**
```bash
python manage.py generate_budget_simulations
```

**Default batch size:** 3 simulations

**Example:**
```bash
python manage.py generate_budget_simulations --batch 5 --category CRD --difficulty I --ai claude
```

### 5. Match and Drag Exercises

Generates sets of related financial terms and definitions that students need to match correctly.

**Usage:**
```bash
python manage.py generate_match_drag
```

**Default batch size:** 3 exercises

**Example:**
```bash
python manage.py generate_match_drag --batch 4 --category INV --difficulty A
```

## Random Category Feature

If you don't specify a `--category` option, the commands will automatically select a random category for each API call:

```bash
# Generate 3 batches with random categories for each call
python manage.py generate_mc_questions --max 3

# Generate match and drag exercises with random categories
python manage.py generate_match_drag --max 6 --batch 2
```

This randomization happens for every batch regardless of batch size, ensuring maximum diversity in your content.

Benefits:
- Creates highly diverse educational content
- Ensures balanced coverage across all financial topics
- Automates generation of a complete curriculum with varied topics
- Each API call gets a fresh random category when no category is specified

## Interactive Mode

All commands support an interactive mode (the default) where you can review content before adding it to the database:

1. The generated content will be displayed with all relevant details.
2. You'll be prompted to accept or reject items:
   - Press Enter to accept all items
   - Enter specific numbers to reject (e.g., `1, 3, 5`)
   - Enter `all` to reject the entire batch

## Bulk Generation

To generate a large amount of content at once, you can use the `--max` option with `--no-input`:

```bash
# Generate 100 multiple choice questions (10 batches of 10)
python manage.py generate_mc_questions --batch 10 --max 10 --no-input

# Generate 50 fill-in-the-blank questions (5 batches of 10)
python manage.py generate_fib_questions --batch 10 --max 5 --no-input

# Generate 200 flash cards (10 batches of 20)
python manage.py generate_flash_cards --batch 20 --max 10 --no-input

# Generate 30 budget simulations (10 batches of 3)
python manage.py generate_budget_simulations --batch 3 --max 10 --no-input

# Generate 20 match and drag exercises (10 batches of 2)
python manage.py generate_match_drag --batch 2 --max 10 --no-input
```

Combine with multiple batches for maximum diversity:

```bash
# Generate content across a variety of categories
python manage.py generate_mc_questions --batch 10 --max 6 --no-input
python manage.py generate_match_drag --batch 3 --max 6 --no-input
```

## Duplicate Detection

All commands include logic to detect and skip duplicate or highly similar content, ensuring that your database doesn't contain repetitive material.

## Recommendations

For the best results:

1. **Start with dry runs** to evaluate quality:
   ```bash
   python manage.py generate_match_drag --dry-run
   ```

2. **Generate content across all categories and difficulties**:
   ```bash
   for cat in BUD INV SAV BAL CRD TAX; do
     for diff in B I A; do
       python manage.py generate_match_drag --category $cat --difficulty $diff --batch 2
     done
   done
   ```

3. **Use multiple batches for diverse content**:
   ```bash
   python manage.py generate_fib_questions --max 6 --batch 5
   ```

4. **Use Claude for more nuanced content** and OpenAI for factual content:
   ```bash
   python manage.py generate_match_drag --ai claude  # Complex term relationships
   python manage.py generate_flash_cards --ai openai  # Factual statements
   ```

5. **Save API costs** by generating small batches first, then scaling up once satisfied with quality:
   ```bash
   # Test with a small batch
   python manage.py generate_match_drag --batch 1 --dry-run
   
   # Generate a larger batch once satisfied
   python manage.py generate_match_drag --batch 3 --max 5 --no-input
   ```

## Creating a Complete Curriculum

You can use these commands together to create a comprehensive financial literacy curriculum:

```bash
# Basic curriculum generation script
for cat in BUD INV SAV BAL CRD TAX; do
  # Generate 10 multiple choice questions per category
  python manage.py generate_mc_questions --category $cat --batch 5 --max 2 --no-input
  
  # Generate 5 fill-in-the-blank questions per category
  python manage.py generate_fib_questions --category $cat --batch 5 --max 1 --no-input
  
  # Generate 10 flash cards per category
  python manage.py generate_flash_cards --category $cat --batch 10 --max 1 --no-input
  
  # Generate 2 budget simulations per category
  python manage.py generate_budget_simulations --category $cat --batch 2 --max 1 --no-input
  
  # Generate 3 match and drag exercises per category
  python manage.py generate_match_drag --category $cat --batch 3 --max 1 --no-input
done
```

This script would generate a complete set of 180 educational content items across all categories and content types.