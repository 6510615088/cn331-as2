from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class UserAuthTests(TestCase):
    
    def setUp(self):
        # Create a normal user
        self.user = User.objects.create_user(username='testuser', password='userpassword')
        
        # Create an admin user
        self.admin_user = User.objects.create_superuser(username='adminuser', password='adminpassword')

    def test_login_page_accessible(self):
        """Test that the login page is accessible with a 200 status code."""
        response = self.client.get(reverse('user_login'))  # Assuming your URL name for login is 'user_login'
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_form_displayed(self):
        """Test that the AuthenticationForm is rendered on the login page."""
        response = self.client.get(reverse('user_login'))
        self.assertIsInstance(response.context['form'], AuthenticationForm)
    
    def test_successful_login_redirects(self):
        """Test that a valid login redirects the user to 'subject_list'."""
        response = self.client.post(reverse('user_login'), {
            'username': 'testuser',
            'password': 'userpassword'
        })
        self.assertRedirects(response, reverse('subject_list'))

    def test_invalid_login(self):
        """Test that an invalid login does not authenticate and re-renders the login form with errors."""
        response = self.client.post(reverse('user_login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        # Check that it re-renders the form
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_user_logout(self):
        """Test that a normal user can log out successfully."""
        self.client.login(username='testuser', password='userpassword')
        response = self.client.get(reverse('user_logout'))
        self.assertRedirects(response, reverse('user_login'))  # Redirect to login after logout
        
    def test_admin_login_page_accessible(self):
        """Test that the admin login page is accessible with a 200 status code."""
        response = self.client.get(reverse('admin_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_login.html')

    def test_successful_admin_login(self):
        """Test that an admin user can log in and is redirected to 'admin_dashboard'."""
        response = self.client.post(reverse('admin_login'), {
            'username': 'adminuser',
            'password': 'adminpassword'
        })
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_non_admin_login_failure(self):
        """Test that a non-admin user cannot log in and gets an error message."""
        response = self.client.post(reverse('admin_login'), {
            'username': 'testuser',
            'password': 'userpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_login.html')
        self.assertContains(response, 'Invalid username or password or not an admin')
