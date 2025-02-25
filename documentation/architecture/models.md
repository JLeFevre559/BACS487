# Database Models

## User Models

### Cap_Ace_User

Extends Django's AbstractUser to provide custom functionality for the financial education platform.

```python
class Cap_Ace_User(AbstractUser):
    CATEGORIES = [
        ('MC', 'Multiple Choice'),
        ('FIB', 'Fill in Blank'),
        ('MAD', 'Match and Drag'),
        ('FC', 'Flash Card'),
        ('BS', 'Budget Simulation')
    ]
    
    last_done = models.CharField(
        max_length=3,
        choices=CATEGORIES,
        null=True,
        blank=True
    )

    # Experience points
    budget_xp = models.IntegerField(default=0)
    investing_xp = models.IntegerField(default=0)
    savings_xp = models.IntegerField(default=0)
    balance_sheet_xp = models.IntegerField(default=0)
    credit_xp = models.IntegerField(default=0)
    taxes_xp = models.IntegerField(default=0)
```

#### Fields
- All fields from Django's AbstractUser
- `last_done`: Tracks the most recent learning activity
- Category-specific experience points fields

## Learning Content Models

### MultipleChoice

Represents a multiple choice question in the learning system.

```python
class MultipleChoice(models.Model):
    DIFFICULTIES = [
        ('B', 'Beginner'),
        ('I', 'Intermediate'),
        ('A', 'Advanced')
    ]

    CATEGORIES = [
        ('BUD', 'Budgeting'),
        ('INV', 'Investing'),
        ('SAV', 'Savings'),
        ('BAL', 'Balance Sheet'),
        ('CRD', 'Credit'),
        ('TAX', 'Taxes')
    ]

    category = models.CharField(max_length=100, choices=CATEGORIES)
    question = models.TextField()
    answer = models.TextField()
    feedback = models.TextField()
    difficulty = models.CharField(max_length=1, choices=DIFFICULTIES, default='B')
```

### MultipleChoiceDistractor

Stores incorrect options for multiple choice questions.

```python
class MultipleChoiceDistractor(models.Model):
    question = models.ForeignKey(MultipleChoice, on_delete=models.CASCADE, related_name='distractors')
    distractor = models.TextField()
```

## Progress Tracking Models

### QuestionProgress

Tracks user progress through learning content.

```python
class QuestionProgress(models.Model):
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

    user = models.ForeignKey(Cap_Ace_User, on_delete=models.CASCADE)
    question_id = models.IntegerField()
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES)
    category = models.CharField(max_length=3, choices=CATEGORIES, null=True)
    completed_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        unique_together = ['user', 'question_id', 'question_type']
```

## Financial Planning Models

### SavingModule

Defines educational modules for savings education.

```python
class SavingModule(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

### SavingsGoal

Tracks user-specific savings goals.

```python
class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    goal_date = models.DateField()
```


## Database Relationships

- `Cap_Ace_User` ←1:N→ `QuestionProgress`
- `MultipleChoice` ←1:N→ `MultipleChoiceDistractor`

## Model Validation

Each model includes appropriate validation:
- Choices fields are restricted to predefined options
- Decimal fields have specified precision
- Foreign key relationships maintain referential integrity
- Unique constraints prevent duplicate entries

## Usage Examples

```python
# Creating a new multiple choice question
question = MultipleChoice.objects.create(
    category='BUD',
    question='What is a budget?',
    answer='A financial plan for spending and saving',
    feedback='A budget helps track income and expenses',
    difficulty='B'
)

# Adding distractors
MultipleChoiceDistractor.objects.create(
    question=question,
    distractor='A type of bank account'
)

# Tracking user progress
QuestionProgress.objects.create(
    user=user,
    question_id=question.id,
    question_type='MC',
    category='BUD'
)
```