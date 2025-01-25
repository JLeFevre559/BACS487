from django.test import TestCase, Client
from django.contrib.auth import authenticate
from .models import Cap_Ace_User as User  # This should be the only User reference

class MultipleChoiceTest(TestCase):
    def setUp(self):
        # Create a test multiple choice question
        self.mc_question = MultipleChoice.objects.create(
            category="Math",
            question="What is 2 + 2?",
            answer="4",
            feedback="Basic addition"
        )
        
        # Create some distractors
        self.distractors = [
            MultipleChoiceDistractor.objects.create(
                question=self.mc_question,
                distractor=str(i)
            ) for i in [3, 5, 6]  # Wrong answers
        ]
        
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

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

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.urls import reverse

class UserAuthenticationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_user_creation(self):
        """Test that we can create a user with our custom User model"""
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
        
        updated_user = User.objects.get(username='testuser')
        self.assertEqual(updated_user.last_done, 'MC')
        
    def test_invalid_category(self):
        """Test that invalid categories are not allowed"""
        with self.assertRaises(Exception):
            self.test_user.last_done = 'INVALID'
            self.test_user.save()
            
    def test_username_unique(self):
        """Test that usernames must be unique"""
        with self.assertRaises(Exception):
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
