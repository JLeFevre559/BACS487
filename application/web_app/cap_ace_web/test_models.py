from django.test import TestCase, Client
from django.contrib.auth import authenticate, get_user_model
from django.apps import apps
from .models import (MultipleChoice, MultipleChoiceDistractor, QuestionProgress, BudgetSimulation, Expense,
                     FlashCard)
from django.db import models
from decimal import Decimal
from django.core.exceptions import ValidationError

class MultipleChoiceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Get the user model
        User = get_user_model()
        
        # Create the test user
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create a test multiple choice question
        cls.mc_question = MultipleChoice.objects.create(
            category="Math",
            question="What is 2 + 2?",
            answer="4",
            feedback="Basic addition"
        )
        
        # Create some distractors
        cls.distractors = [
            MultipleChoiceDistractor.objects.create(
                question=cls.mc_question,
                distractor=str(i)
            ) for i in [3, 5, 6]
        ]

    def setUp(self):
        # No need to create objects here anymore
        pass

    def test_question_creation(self):
        """Test that a question can be created with proper attributes"""
        self.assertEqual(self.mc_question.category, "Math")
        self.assertEqual(self.mc_question.question, "What is 2 + 2?")
        self.assertEqual(self.mc_question.answer, "4")
        self.assertEqual(self.mc_question.feedback, "Basic addition")

    def test_distractors_relationship(self):
        """Test that distractors are properly linked to the question"""
        distractors = self.mc_question.distractors.all()
        self.assertEqual(distractors.count(), 3)
        self.assertIn(self.distractors[0], distractors)
        
    def test_get_all_options(self):
        """Test getting all options (correct answer + distractors) for a question"""
        all_distractors = [d.distractor for d in self.mc_question.distractors.all()]
        all_options = all_distractors + [self.mc_question.answer]
        self.assertEqual(len(all_options), 4)  # 3 distractors + 1 correct answer
        self.assertIn("4", all_options)  # Correct answer is present
        self.assertIn("3", all_options)  # Distractor is present
        
    def test_mark_question_completed(self):
        """Test marking a question as completed for a user"""
        # Create progress record
        progress = QuestionProgress.objects.create(
            user=self.user,
            question_id=self.mc_question.id,
            question_type='MC'
        )
        
        # Check if progress was recorded
        user_progress = QuestionProgress.objects.filter(
            user=self.user,
            question_id=self.mc_question.id,
            question_type='MC'
        ).exists()
        
        self.assertTrue(user_progress)
        
    def test_unique_progress_constraint(self):
        """Test that duplicate progress entries are not allowed"""
        # Create initial progress
        QuestionProgress.objects.create(
            user=self.user,
            question_id=self.mc_question.id,
            question_type='MC'
        )
        
        # Attempt to create duplicate progress
        with self.assertRaises(Exception):
            QuestionProgress.objects.create(
                user=self.user,
                question_id=self.mc_question.id,
                question_type='MC'
            )
            
    def test_question_str_method(self):
        """Test the string representation of the question"""
        expected_str = f"Multiple Choice: What is 2 + 2?..."
        self.assertEqual(str(self.mc_question), expected_str)

    def test_distractor_str_method(self):
        """Test the string representation of a distractor"""
        distractor = self.distractors[0]
        expected_str = f"Distractor for {self.mc_question.id}: {distractor.distractor}"
        self.assertEqual(str(distractor), expected_str)

class UserAuthenticationTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = Client()
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_user_creation(self):
        """Test that we can create a user with our custom User model"""
        User = get_user_model()
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIsNone(user.last_done)
        
    def test_user_authentication(self):
        """Test that created users can authenticate"""
        user = authenticate(username='testuser', password='testpass123')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')
        
    def test_wrong_password(self):
        """Test that authentication fails with wrong password"""
        user = authenticate(username='testuser', password='wrongpass')
        self.assertIsNone(user)
        
    def test_create_superuser(self):
        """Test creation of superuser"""
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)
        
    def test_last_done_update(self):
        """Test updating the last_done field"""
        self.test_user.last_done = 'MC'
        self.test_user.save()

        User = get_user_model()
        
        updated_user = User.objects.get(username='testuser')
        self.assertEqual(updated_user.last_done, 'MC')
        
    def test_invalid_category(self):
        """Test that invalid categories are not allowed"""
        with self.assertRaises(Exception):
            self.test_user.last_done = 'INVALID'
            self.test_user.full_clean()
            self.test_user.save()
            
    def test_username_unique(self):
        """Test that usernames must be unique"""
        with self.assertRaises(Exception):
            User = get_user_model()
            User.objects.create_user(
                username='testuser',  # This username already exists
                password='anotherpass123'
            )
            
    def test_user_inactive(self):
        """Test that inactive users cannot authenticate"""
        self.test_user.is_active = False
        self.test_user.save()
        user = authenticate(username='testuser', password='testpass123')
        self.assertIsNone(user)

class QuestionProgressTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Get the user model
        User = get_user_model()
        
        # Create the test user
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create a test multiple choice question
        cls.mc_question = MultipleChoice.objects.create(
            category="Budgeting",
            question="What is a budget?",
            answer="A financial plan for spending and saving",
            feedback="Budgeting is essential for financial planning"
        )

    def test_progress_creation(self):
        """Test creating a progress record with category"""
        progress = QuestionProgress.objects.create(
            user=self.user,
            question_id=self.mc_question.id,
            question_type='MC',
            category='BUD'
        )
        
        self.assertEqual(progress.category, 'BUD')
        self.assertEqual(progress.get_category_display(), 'Budgeting')
        
    def test_invalid_category(self):
        """Test that invalid categories are not allowed"""
        with self.assertRaises(Exception):
            qp = QuestionProgress.objects.create(
                user=self.user,
                question_id=self.mc_question.id,
                question_type='MC',
                category='INVALID'
            )
            qp.full_clean()

            
    def test_unique_progress_constraint(self):
        """Test that duplicate progress entries are not allowed"""
        # Create initial progress
        QuestionProgress.objects.create(
            user=self.user,
            question_id=self.mc_question.id,
            question_type='MC',
            category='BUD'
        )
        
        # Attempt to create duplicate progress
        with self.assertRaises(Exception):
            QuestionProgress.objects.create(
                user=self.user,
                question_id=self.mc_question.id,
                question_type='MC',
                category='BUD'
            )
            
    def test_progress_str_method(self):
        """Test the string representation of the progress"""
        progress = QuestionProgress.objects.create(
            user=self.user,
            question_id=self.mc_question.id,
            question_type='MC',
            category='BUD'
        )
        expected_str = f"testuser - Budgeting - Multiple Choice {self.mc_question.id}"
        self.assertEqual(str(progress), expected_str)
        
    def test_category_specific_progress(self):
        """Test retrieving progress for specific categories"""
        # Create progress records for different categories
        QuestionProgress.objects.create(
            user=self.user,
            question_id=1,
            question_type='MC',
            category='BUD'
        )
        QuestionProgress.objects.create(
            user=self.user,
            question_id=2,
            question_type='MC',
            category='SAV'
        )
        
        budgeting_progress = QuestionProgress.objects.filter(
            user=self.user,
            category='BUD'
        ).count()
        savings_progress = QuestionProgress.objects.filter(
            user=self.user,
            category='SAV'
        ).count()
        
        self.assertEqual(budgeting_progress, 1)
        self.assertEqual(savings_progress, 1)

User = get_user_model()
class SavingModule(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    goal_date = models.DateField()
# class BudgetCategory(models.Model):
#     name = models.CharField(max_length=100)

# class Expense(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     category = models.ForeignKey(BudgetCategory, on_delete=models.CASCADE)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     date = models.DateField(auto_now_add=True)

class BudgetSimulationModelTests(TestCase):
    def setUp(self):
        """Set up test data."""
        # Create a budget simulation with valid data
        self.budget_sim = BudgetSimulation.objects.create(
            question="Create a monthly budget for a student",
            monthly_income=Decimal('2000.00'),
            difficulty='B'
        )
        
        # Add expenses
        self.rent = Expense.objects.create(
            BudgetSimulation=self.budget_sim,
            name="Rent",
            amount=Decimal('800.00'),
            feedback="Consider getting roommates to reduce costs.",
            essential=True
        )
        
        self.groceries = Expense.objects.create(
            BudgetSimulation=self.budget_sim,
            name="Groceries",
            amount=Decimal('300.00'),
            feedback="Buy in bulk to save money.",
            essential=True
        )
        
        self.entertainment = Expense.objects.create(
            BudgetSimulation=self.budget_sim,
            name="Entertainment",
            amount=Decimal('150.00'),
            feedback="Look for free entertainment options.",
            essential=False
        )

    def test_budget_simulation_creation(self):
        """Test that a budget simulation can be created with valid data."""
        self.assertEqual(self.budget_sim.question, "Create a monthly budget for a student")
        self.assertEqual(self.budget_sim.monthly_income, Decimal('2000.00'))
        self.assertEqual(self.budget_sim.difficulty, 'B')
        
    def test_expense_creation(self):
        """Test that expenses can be created and associated with a budget simulation."""
        self.assertEqual(self.rent.name, "Rent")
        self.assertEqual(self.rent.amount, Decimal('800.00'))
        self.assertTrue(self.rent.essential)
        
        # Test relationship from budget sim to expenses
        expenses = self.budget_sim.expenses.all()
        self.assertEqual(expenses.count(), 3)
    
    def test_expense_string_representation(self):
        """Test the string representation of an expense."""
        self.assertEqual(str(self.rent), "Rent: $800.00 (Essential)")
        self.assertEqual(str(self.entertainment), "Entertainment: $150.00")
    
    def test_valid_essential_expenses(self):
        """Test that a budget simulation with valid essential expenses passes validation."""
        # Current essential expenses total: $1100 (rent + groceries)
        # Monthly income: $2000
        # Should be valid
        self.budget_sim.clean()  # Should not raise ValidationError
    
    def test_invalid_essential_expenses(self):
        """Test that a budget simulation with invalid essential expenses fails validation."""
        # Add another essential expense that pushes total over income
        transportation = Expense.objects.create(
            BudgetSimulation=self.budget_sim,
            name="Transportation",
            amount=Decimal('1000.00'),
            feedback="Consider public transportation.",
            essential=True
        )
        
        # Now essential expenses total: $2100 (rent + groceries + transportation)
        # Monthly income: $2000
        # Should be invalid
        with self.assertRaises(ValidationError):
            self.budget_sim.clean()
    
    def test_changing_expense_to_essential(self):
        """Test validation when changing a non-essential expense to essential."""
        # Change entertainment from non-essential to essential
        self.entertainment.essential = True
        self.entertainment.save()
        
        # Now essential expenses total: $1250 (rent + groceries + entertainment)
        # Monthly income: $2000
        # Should still be valid
        self.budget_sim.clean()  # Should not raise ValidationError
        
        # Now increase entertainment amount to push over limit
        self.entertainment.amount = Decimal('1000.00')
        self.entertainment.save()
        
        # Now essential expenses total: $2100 (rent + groceries + entertainment)
        # Should be invalid
        with self.assertRaises(ValidationError):
            self.budget_sim.clean()
    
    def test_update_monthly_income(self):
        """Test validation when updating monthly income."""
        # Reduce monthly income to less than essential expenses
        self.budget_sim.monthly_income = Decimal('1000.00')
        
        # Now essential expenses total: $1100 (rent + groceries)
        # Monthly income: $1000
        # Should be invalid
        with self.assertRaises(ValidationError):
            self.budget_sim.clean()
        
        # Increase monthly income to valid level
        self.budget_sim.monthly_income = Decimal('1200.00')
        # Should now be valid
        self.budget_sim.clean()  # Should not raise ValidationError
    
    def test_exactly_equal_income_and_essential_expenses(self):
        """Test validation when essential expenses exactly equal monthly income."""
        # Set monthly income to exactly match essential expenses
        self.budget_sim.monthly_income = Decimal('1100.00')  # Equal to rent + groceries
        
        # Should be valid when exactly equal
        self.budget_sim.clean()  # Should not raise ValidationError


class ExpenseModelTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.budget_sim = BudgetSimulation.objects.create(
            question="Create a monthly budget for a family",
            monthly_income=Decimal('5000.00'),
            difficulty='I'
        )
    
    def test_expense_defaults(self):
        """Test that expense defaults are set correctly."""
        expense = Expense.objects.create(
            BudgetSimulation=self.budget_sim,
            name="Test Expense",
            amount=Decimal('100.00'),
            feedback="Test feedback"
        )
        
        # essential should default to False
        self.assertFalse(expense.essential)
    
    def test_expense_decimal_precision(self):
        """Test that expense amount decimal precision is handled correctly."""
        expense = Expense.objects.create(
            BudgetSimulation=self.budget_sim,
            name="Precise Expense",
            amount=Decimal('123.45'),
            feedback="Test precision"
        )
        
        self.assertEqual(expense.amount, Decimal('123.45'))
        
        # Test with more decimal places than the model allows
        expense2 = Expense.objects.create(
            BudgetSimulation=self.budget_sim,
            name="Extra Precision",
            amount=Decimal('123.4567'),
            feedback="Test precision"
        )
        
        # Should be truncated/rounded to 2 decimal places
        retrieved = Expense.objects.get(pk=expense2.pk)
        self.assertEqual(retrieved.amount, Decimal('123.46'))
    
    def test_cascade_deletion(self):
        """Test that expenses are deleted when a budget simulation is deleted."""
        expense = Expense.objects.create(
            BudgetSimulation=self.budget_sim,
            name="To Be Deleted",
            amount=Decimal('100.00'),
            feedback="Test cascade delete"
        )
        
        # Confirm expense exists
        self.assertEqual(Expense.objects.count(), 1)
        
        # Delete the budget simulation
        self.budget_sim.delete()
        
        # Expense should be automatically deleted due to CASCADE
        self.assertEqual(Expense.objects.count(), 0)

class FlashCardModelTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.flashcard = FlashCard.objects.create(
            question="The capital of France is Paris",
            answer=True,
            feedback="Paris is the capital of France.",
            category='GOV',
            difficulty='B'
        )
    
    def test_flashcard_creation(self):
        """Test that a flashcard can be created with valid data."""
        self.assertEqual(self.flashcard.question, "The capital of France is Paris")
        self.assertTrue(self.flashcard.answer)
        self.assertEqual(self.flashcard.feedback, "Paris is the capital of France.")
        self.assertEqual(self.flashcard.category, 'GOV')
        self.assertEqual(self.flashcard.difficulty, 'B')