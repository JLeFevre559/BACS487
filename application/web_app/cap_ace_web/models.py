from django.db import models
from django.contrib.auth.models import User

class MultipleChoice(models.Model):
    category = models.CharField(max_length=100)
    question = models.TextField()
    answer = models.TextField()
    feedback = models.TextField()

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

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question_id = models.IntegerField()
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES)

    class Meta:
        unique_together = ['user', 'question_id', 'question_type']
        
    def __str__(self):
        return f"{self.user.username} - {self.question_type} {self.question_id}"