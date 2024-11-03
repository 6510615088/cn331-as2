from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Subject, UserSubject
from django.db import models


class UserAuthTests(TestCase):

    def setUp(self):
        # Create a normal user
        self.user = User.objects.create_user(
            username='testuser', password='userpassword')
        self.client = Client()
        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username='adminuser', password='adminpassword')
        self.subject = Subject.objects.create(
            name="Math", max_students=2, open_for_registration=True)

    def test_login_page_accessible(self):
        """Test that the login page is accessible with a 200 status code."""
        response = self.client.get(reverse('user_login'))
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
        # Redirect to login after logout
        self.assertRedirects(response, reverse('user_login'))

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
        self.assertContains(
            response, 'Invalid username or password or not an admin')

    def test_register_subject_success(self):
        """Test that a user can register for a subject successfully."""
        response = self.client.get(
            reverse('register_subject', args=[self.subject.id]))
        self.assertRedirects(response, reverse('subject_list'))

        # Check that the user is now registered for the subject
        self.assertTrue(UserSubject.objects.filter(
            user=self.user, subject=self.subject).exists())

        # Check that max_students has decreased by 1
        self.subject.refresh_from_db()
        self.assertEqual(self.subject.max_students, 1)

    def test_register_subject_max_capacity(self):
        """Test that registration is not allowed if max capacity is reached."""
        # Fill up the subject
        self.subject.max_students = 1
        self.subject.save()

        # Attempt to register the user
        response = self.client.get(
            reverse('register_subject', args=[self.subject.id]))

        # User should not be registered
        self.assertFalse(UserSubject.objects.filter(
            user=self.user, subject=self.subject).exists())

        # The user should still be redirected to the subject list, but without registration
        self.assertRedirects(response, reverse('subject_list'))

        # max_students should remain 0 and open_for_registration should be False
        self.subject.refresh_from_db()
        self.assertEqual(self.subject.max_students, 1)
        self.assertFalse(self.subject.open_for_registration)

    def test_unregister_subject_success(self):
        """Test that a user can unregister from a subject successfully."""
        # Register the user for the subject
        UserSubject.objects.create(user=self.user, subject=self.subject)
        self.subject.max_students = 1
        self.subject.open_for_registration = False
        self.subject.save()

        # Unregister the user
        response = self.client.get(
            reverse('unregister_subject', args=[self.subject.id]))
        self.assertRedirects(response, reverse('subject_list'))

        # Ensure the user is no longer registered
        self.assertFalse(UserSubject.objects.filter(
            user=self.user, subject=self.subject).exists())

        # Check that max_students has increased by 1 and open_for_registration is now True
        self.subject.refresh_from_db()
        self.assertEqual(self.subject.max_students, 2)
        self.assertTrue(self.subject.open_for_registration)

    def test_unregister_subject_not_registered(self):
        """Test that unregistering a user who is not registered has no side effects."""
        response = self.client.get(
            reverse('unregister_subject', args=[self.subject.id]))
        self.assertRedirects(response, reverse('subject_list'))

        # Ensure no registration record exists
        self.assertFalse(UserSubject.objects.filter(
            user=self.user, subject=self.subject).exists())

        # Ensure that max_students is unchanged
        self.subject.refresh_from_db()
        self.assertEqual(self.subject.max_students, 2)

    def test_register_and_reach_max_capacity(self):
        """Test that max_students decrements and open_for_registration is set to False at capacity."""
        # Register the user once
        self.client.get(reverse('register_subject', args=[self.subject.id]))

        # Register a second user to reach max capacity
        another_user = User.objects.create_user(
            username='anotheruser', password='password')
        self.client.logout()
        self.client.login(username='anotheruser', password='password')
        self.client.get(reverse('register_subject', args=[self.subject.id]))

        # Refresh and check that max_students is now 0 and open_for_registration is False
        self.subject.refresh_from_db()
        self.assertEqual(self.subject.max_students, 0)
        self.assertFalse(self.subject.open_for_registration)
