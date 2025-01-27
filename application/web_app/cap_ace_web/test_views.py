from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from http import HTTPStatus

User = get_user_model()

class UserViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create a regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create a superuser
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Create another regular user
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )

    def test_create_view(self):
        """Test user creation view"""
        url = reverse('user_create')
        
        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        # Test POST request with valid data
        response = self.client.post(url, {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        self.assertEqual(User.objects.count(), 4)  # Including the ones from setUp
        
        # Test POST request with invalid data
        response = self.client.post(url, {
            'username': 'testuser',  # Already exists
            'email': 'invalid',
            'password1': 'pass',
            'password2': 'different'
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)  # Returns form with errors
        self.assertEqual(User.objects.count(), 4)  # No new user created

    def test_detail_view_permissions(self):
        """Test user detail view permissions"""
        # Test unauthorized access
        url = reverse('user_detail', kwargs={'pk': self.user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)  # Redirect to login
        
        # Test access to own profile
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        # Test access to other's profile (should fail)
        other_url = reverse('user_detail', kwargs={'pk': self.other_user.pk})
        response = self.client.get(other_url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        
        # Test superuser access to other's profile
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(other_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_update_view_permissions(self):
        """Test user update view permissions"""
        url = reverse('user_edit', kwargs={'pk': self.user.pk})
        
        # Test unauthorized access
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)  # Redirect to login
        
        # Test updating own profile
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        # Test updating other's profile (should fail)
        other_url = reverse('user_edit', kwargs={'pk': self.other_user.pk})
        response = self.client.get(other_url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        
        # Test superuser updating other's profile
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(other_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_list_view_permissions(self):
        """Test user list view permissions"""
        url = reverse('user_list')
        
        # Test unauthorized access
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)  # Redirect to login
        
        # Test regular user access (should fail)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        
        # Test superuser access
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'otheruser')

    def test_delete_view_permissions(self):
        """Test user delete view permissions"""
        url = reverse('user_delete', kwargs={'pk': self.user.pk})
        
        # Test unauthorized access
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)  # Redirect to login
        
        # Test regular user access (should fail)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        
        # Test superuser access
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        # Test actual deletion
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)  # Redirect after deletion
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())