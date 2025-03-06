from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from decimal import Decimal

DIFFICULTIES = [
        ('B', 'Beginner'),
        ('I', 'Intermediate'),
        ('A', 'Advanced')
]

    
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

    # Experience points, reduces database calls by storing the total xp in the user model
    budget_xp = models.IntegerField(default=0)
    investing_xp = models.IntegerField(default=0)
    savings_xp = models.IntegerField(default=0)
    balance_sheet_xp = models.IntegerField(default=0)
    credit_xp = models.IntegerField(default=0)
    taxes_xp = models.IntegerField(default=0)

    def __str__(self):
        return self.username

class FillInTheBlank(models.Model):
    
    CATEGORIES = [
        ('BUD', 'Budgeting'),
        ('INV', 'Investing'),
        ('SAV', 'Savings'),
        ('BAL', 'Balance Sheet'),
        ('CRD', 'Credit'),
        ('TAX', 'Taxes')
    ]

    difficulty = models.CharField(max_length=1, choices=DIFFICULTIES, default='B')
    question = models.TextField()
    answer = models.TextField()
    missing_word = models.CharField()
    def __str__(self):
        return f"Fill in the Blank: {self.question}..."


class MultipleChoice(models.Model):
    
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

    def __str__(self):
        return f"Multiple Choice: {self.question}..."
    


class MultipleChoiceDistractor(models.Model):
    question = models.ForeignKey(MultipleChoice, on_delete=models.CASCADE, related_name='distractors')
    distractor = models.TextField()

    def __str__(self):
        return f"Distractor for {self.question.id}: {self.distractor}"
    
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
        
    def __str__(self):
        return f"{self.user.username} - {self.get_category_display()} - {self.get_question_type_display()} {self.question_id}"
    
class BudgetSimulation(models.Model):
    question = models.TextField()
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2)
    difficulty = models.CharField(max_length=1, choices=DIFFICULTIES, default='B')

    def clean(self):
        """
        Validate that the sum of essential expenses is less than the monthly income.
        This method is called during model validation, both through Model.full_clean()
        and when saving an instance through the admin.
        """
        super().clean()
        
        # Skip validation for new instances without an ID yet
        if not self.pk:
            return
            
        # Calculate sum of essential expenses
        essential_expenses_sum = Decimal('0.00')
        for expense in self.expenses.filter(essential=True):
            essential_expenses_sum += expense.amount
            
        # Validate that essential expenses don't exceed monthly income
        if essential_expenses_sum > self.monthly_income:
            raise ValidationError(
                f"The sum of essential expenses (${essential_expenses_sum}) exceeds the monthly income (${self.monthly_income}). "
                f"Either increase the monthly income or reduce essential expenses."
            )
    
    def save(self, *args, **kwargs):
        self.full_clean()  # Run validation before saving
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Budget Simulation: {self.question[:50]}..."

class Expense(models.Model):
    BudgetSimulation = models.ForeignKey(BudgetSimulation, on_delete=models.CASCADE, related_name='expenses')
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    feedback = models.TextField()
    essential = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}: ${self.amount}" + (" (Essential)" if self.essential else "")
