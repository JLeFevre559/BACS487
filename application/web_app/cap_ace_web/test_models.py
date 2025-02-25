from django.test import TestCase, Client
from django.contrib.auth import authenticate, get_user_model
from django.apps import apps
from .models import MultipleChoice, MultipleChoiceDistractor, QuestionProgress
from django.db import models

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
class BudgetCategory(models.Model):
    name = models.CharField(max_length=100)

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(BudgetCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
