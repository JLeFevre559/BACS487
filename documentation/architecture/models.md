# Database Models

## User Models

### Cap_Ace_User

Extends Django's AbstractUser to provide custom functionality for the financial education platform.

```python
class Cap_Ace_User(AbstractUser):
    last_done = models.CharField(
        max_length=3,
        choices=QUESTION_TYPES,
        null=True,
        blank=True
    )

    # Experience points, reduces database calls by storing the total xp in the user model
    budget_xp = models.IntegerField(default=0)
    investing_xp = models.IntegerField(default=0)
    savings_xp = models.IntegerField(default=0)
    balance_sheet_xp = models.IntegerField(default=0)
    credit_xp = models.IntegerField(default=0)
    taxes_xp = models.IntegerField(default=0)
```

#### Fields
- All fields from Django's AbstractUser
- `last_done`: Tracks the most recent learning activity type
- Category-specific experience points fields for tracking user progress in different financial topics

## Common Choices

The following choices are used across multiple models:

```python
DIFFICULTIES = [
    ('B', 'Beginner'),
    ('I', 'Intermediate'),
    ('A', 'Advanced')
]

QUESTION_TYPES = [
    ('MC', 'Multiple Choice'),
    ('FIB', 'Fill in Blank'),
    ('MAD', 'Match and Drag'),
    ('FC', 'Flash Card'),
    ('BS', 'Budget Simulation')
]

CATEGORIES = [
    ('BUD', 'Budgeting'),
    ('INV', 'Investing'),
    ('SAV', 'Savings'),
    ('BAL', 'Balance Sheet'),
    ('CRD', 'Credit'),
    ('TAX', 'Taxes')
]
```

## Learning Content Models

### FillInTheBlank

Represents a fill-in-the-blank question type.

```python
class FillInTheBlank(models.Model):
    difficulty = models.CharField(max_length=1, choices=DIFFICULTIES, default='B')
    question = models.TextField()
    answer = models.TextField()
    missing_word = models.CharField(max_length=100)
    feedback = models.TextField(default="")
    category = models.CharField(max_length=3, choices=CATEGORIES, null=True)
```

#### Fields
- `difficulty`: The complexity level of the question
- `question`: The full text of the question with a blank space
- `answer`: The correct response
- `missing_word`: The specific word that should fill the blank
- `feedback`: Educational feedback for the user
- `category`: The financial topic this question belongs to

### MultipleChoice

Represents a multiple choice question in the learning system.

```python
class MultipleChoice(models.Model):
    category = models.CharField(max_length=100, choices=CATEGORIES)
    question = models.TextField()
    answer = models.TextField()
    feedback = models.TextField()
    difficulty = models.CharField(max_length=1, choices=DIFFICULTIES, default='B')
```

#### Fields
- `category`: The financial topic this question belongs to
- `question`: The text of the question
- `answer`: The correct response
- `feedback`: Educational feedback for the user
- `difficulty`: The complexity level of the question

### MultipleChoiceDistractor

Stores incorrect options for multiple choice questions.

```python
class MultipleChoiceDistractor(models.Model):
    question = models.ForeignKey(MultipleChoice, on_delete=models.CASCADE, related_name='distractors')
    distractor = models.TextField()
```

#### Fields
- `question`: Foreign key to the parent MultipleChoice question
- `distractor`: An incorrect option for the question

### FlashCard

Represents a true/false flashcard question.

```python
class FlashCard(models.Model):
    question = models.CharField(max_length=100)
    answer = models.BooleanField(default=False)
    feedback = models.TextField()
    category = models.CharField(max_length=3, choices=CATEGORIES, null=True)
    difficulty = models.CharField(max_length=1, choices=DIFFICULTIES, default='B')
```

#### Fields
- `question`: The text of the flashcard question
- `answer`: Boolean value indicating whether the statement is true or false
- `feedback`: Educational feedback explaining the correct answer
- `category`: The financial topic this flashcard belongs to
- `difficulty`: The complexity level of the flashcard

## Progress Tracking Models

### QuestionProgress

Tracks user progress through learning content.

```python
class QuestionProgress(models.Model):
    user = models.ForeignKey(Cap_Ace_User, on_delete=models.CASCADE)
    question_id = models.IntegerField()
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES)
    category = models.CharField(max_length=3, choices=CATEGORIES, null=True)
    completed_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        unique_together = ['user', 'question_id', 'question_type']
```

#### Fields
- `user`: Foreign key to the user completing the question
- `question_id`: Reference to the specific question
- `question_type`: Type of question (MC, FIB, etc.)
- `category`: The financial topic of the question
- `completed_at`: Timestamp when the question was completed

## Financial Planning Models

### BudgetSimulation

Provides interactive budget simulation exercises with validation to ensure users can complete the simulation.

```python
class BudgetSimulation(models.Model):
    question = models.TextField()
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2)
    difficulty = models.CharField(max_length=1, choices=DIFFICULTIES, default='B')
    category = models.CharField(max_length=3, choices=CATEGORIES, null=True, default='BUD')
    
    def clean(self):
        # Validates that essential expenses don't exceed monthly income
        super().clean()
        
        if not self.pk:
            return
            
        essential_expenses_sum = Decimal('0.00')
        for expense in self.expenses.filter(essential=True):
            essential_expenses_sum += expense.amount
            
        if essential_expenses_sum > self.monthly_income:
            raise ValidationError(
                f"The sum of essential expenses (${essential_expenses_sum}) exceeds the monthly income (${self.monthly_income}). "
                f"Either increase the monthly income or reduce essential expenses."
            )
    
    def save(self, *args, **kwargs):
        self.full_clean()  # Run validation before saving
        super().save(*args, **kwargs)
```

#### Fields
- `question`: The prompt or scenario for the budget simulation
- `monthly_income`: The simulated income amount
- `difficulty`: The complexity level of the simulation
- `category`: The financial topic this simulation belongs to (defaults to 'BUD' for Budgeting)

#### Validation Behavior
- Enforces that the sum of all essential expenses must be less than the monthly income
- Validates both when creating new simulations and when updating existing ones
- Ensures realistic budget scenarios for educational purposes

### Expense

Represents individual expenses within a budget simulation.

```python
class Expense(models.Model):
    BudgetSimulation = models.ForeignKey(BudgetSimulation, on_delete=models.CASCADE, related_name='expenses')
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    feedback = models.TextField(help_text="Provide feedback on why this expense is or isn't essential")
    essential = models.BooleanField(default=False)
```

#### Fields
- `BudgetSimulation`: Foreign key to the parent simulation
- `name`: Description of the expense
- `amount`: Monetary value of the expense
- `feedback`: Educational feedback about this expense type
- `essential`: Flag indicating if the expense is essential (must be covered by income)

## Database Relationships

- `Cap_Ace_User` ←1:N→ `QuestionProgress`
- `MultipleChoice` ←1:N→ `MultipleChoiceDistractor`
- `BudgetSimulation` ←1:N→ `Expense`

## Model Validation

Each model includes appropriate validation:
- Choices fields are restricted to predefined options
- Decimal fields have specified precision
- Foreign key relationships maintain referential integrity
- Unique constraints prevent duplicate entries
- BudgetSimulation validates that essential expenses don't exceed monthly income

## Usage Examples

```python
# Creating a fill in the blank question
fib_question = FillInTheBlank.objects.create(
    difficulty='B',
    question='A financial plan that allocates future income toward expenses, savings, and debt repayment is called a ______.',
    answer='budget',
    missing_word='budget',
    feedback='A budget is a foundational tool for managing your finances effectively.',
    category='BUD'
)

# Creating a multiple choice question
mc_question = MultipleChoice.objects.create(
    category='INV',
    question='Which of the following is typically considered the safest investment?',
    answer='U.S. Treasury Bonds',
    feedback='U.S. Treasury Bonds are backed by the full faith and credit of the U.S. government, making them one of the safest investments available.',
    difficulty='B'
)

# Adding distractors
MultipleChoiceDistractor.objects.create(
    question=mc_question,
    distractor='Cryptocurrency'
)
MultipleChoiceDistractor.objects.create(
    question=mc_question,
    distractor='Individual Stocks'
)
MultipleChoiceDistractor.objects.create(
    question=mc_question,
    distractor='Commodities Futures'
)

# Creating a flashcard
flashcard = FlashCard.objects.create(
    question='A credit score above 700 is generally considered good.',
    answer=True,
    feedback='Credit scores typically range from 300-850, with scores above 700 generally considered good and providing access to better interest rates.',
    category='CRD',
    difficulty='B'
)

# Creating a budget simulation
simulation = BudgetSimulation.objects.create(
    question='Create a monthly budget for a new college graduate with a starting salary of $48,000 per year.',
    monthly_income=4000.00,  # $48,000 / 12
    difficulty='I',
    category='BUD'
)

# Adding expenses to the simulation
Expense.objects.create(
    BudgetSimulation=simulation,
    name='Rent',
    amount=1200.00,
    feedback='Housing costs should typically be kept under 30% of your monthly income.',
    essential=True
)

Expense.objects.create(
    BudgetSimulation=simulation,
    name='Student Loan Payment',
    amount=350.00,
    feedback='Paying student loans on time is important for building credit history.',
    essential=True
)

Expense.objects.create(
    BudgetSimulation=simulation,
    name='Dining Out',
    amount=250.00,
    feedback='While social activities are important, consider balancing dining out with home cooking to save money.',
    essential=False
)

# Tracking user progress
user = Cap_Ace_User.objects.get(username='learner123')
QuestionProgress.objects.create(
    user=user,
    question_id=mc_question.id,
    question_type='MC',
    category='INV',
    completed_at=timezone.now()
)

# Update user experience points
user.investing_xp += 10
user.save()
```