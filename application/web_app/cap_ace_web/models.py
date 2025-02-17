from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

    
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
