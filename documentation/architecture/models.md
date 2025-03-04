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

### BudgetSimulation

Provides interactive budget simulation exercises with validation to ensure users can complete the simulation.

```python
class BudgetSimulation(models.Model):
    DIFFICULTIES = [
        ('B', 'Beginner'),
        ('I', 'Intermediate'),
        ('A', 'Advanced')
    ]
    
    question = models.TextField()
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2)
    difficulty = models.CharField(max_length=1, choices=DIFFICULTIES, default='B')
    
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
                f"The sum of essential expenses (${essential_expenses_sum}) exceeds the monthly income (${self.monthly_income})."
            )
    
    def save(self, *args, **kwargs):
        self.full_clean()  # Run validation before saving
        super().save(*args, **kwargs)
```

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
    feedback = models.TextField()
    essential = models.BooleanField(default=False)
```

#### Fields
- `BudgetSimulation`: Foreign key to the parent simulation
- `name`: Description of the expense
- `amount`: Monetary value of the expense
- `feedback`: Educational feedback to provide to the user
- `essential`: Flag indicating if the expense is essential (must be covered by income)

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
- `BudgetSimulation` ←1:N→ `Expense`

## Model Validation

Each model includes appropriate validation:
- Choices fields are restricted to predefined options
- Decimal fields have specified precision
- Foreign key relationships maintain referential integrity
- Unique constraints prevent duplicate entries
- BudgetSimulation validates that essential expenses don't exceed monthly income

## Admin Interface Customization

The BudgetSimulation admin interface includes:
- Custom validation in the ExpenseInlineFormSet to validate the essential expenses sum
- Display of the essential expenses sum in the list view
- Warning messages when validation rules are violated

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

# Creating a budget simulation
simulation = BudgetSimulation.objects.create(
    question='Create a budget for a college student with a part-time job',
    monthly_income=1500.00,
    difficulty='B'
)

# Adding expenses to the simulation
Expense.objects.create(
    BudgetSimulation=simulation,
    name='Rent',
    amount=800.00,
    feedback='Housing is typically the largest expense in a budget',
    essential=True
)

Expense.objects.create(
    BudgetSimulation=simulation,
    name='Groceries',
    amount=300.00,
    feedback='Meal planning can help reduce food costs',
    essential=True
)

Expense.objects.create(
    BudgetSimulation=simulation,
    name='Entertainment',
    amount=100.00,
    feedback='Entertainment is important but should be budgeted carefully',
    essential=False
)

# Tracking user progress
QuestionProgress.objects.create(
    user=user,
    question_id=question.id,
    question_type='MC',
    category='BUD'
)
```