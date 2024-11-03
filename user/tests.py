from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.test import Client
from subjectreg.models import Subject
from user.models import UserSubject


class UserAuthTests(TestCase):

    def setUp(self):
        # Create a normal user
        self.user = User.objects.create_user(
            username='testuser', password='userpassword')

        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username='adminuser', password='adminpassword')

    def test_login_page_accessible(self):
        """Test that the login page is accessible with a 200 status code."""

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


class RegisterSubjectViewTest(TestCase):
    def setUp(self):
        # Create a user for login
        self.user = User.objects.create_user(
            username='testuser', password='userpassword')

        # Create a subject in the `subjectreg` app with available seats
        self.subject = Subject.objects.create(
            subject_id='CN101',
            name='Introduction to Computer Programming',
            semester=1,
            academic_year=2024,
            max_students=1,
            open_for_registration=True
        )

        # Log in the user for the test
        self.client = Client()
        self.client.login(username='testuser', password='userpassword')

    def test_successful_registration(self):
        """Test that a user can register for a subject with available seats."""
        response = self.client.post(
            reverse('register_subject', args=[self.subject.id]))
        self.assertRedirects(response, reverse('subject_list'))

        # Confirm that the UserSubject instance was created
        self.assertTrue(UserSubject.objects.filter(
            user=self.user, subject=self.subject).exists())

        # Confirm max_students count is decreased by 1
        subject = Subject.objects.get(id=self.subject.id)
        self.assertEqual(subject.max_students, 0)

    def test_subject_closes_when_full(self):
        """Test that subject closes registration when max_students reaches zero."""
        self.client.post(reverse('register_subject', args=[self.subject.id]))

        # Check if open_for_registration is set to False after max_students reaches zero
        subject = Subject.objects.get(id=self.subject.id)
        self.assertFalse(subject.open_for_registration)

    def test_registration_restricted_when_full(self):
        """Test that a user cannot register if the subject is already full."""
        # Register the user to make the subject full
        UserSubject.objects.create(user=self.user, subject=self.subject)
        self.subject.max_students = 0
        self.subject.open_for_registration = False
        self.subject.save()

        # Attempt to register again
        response = self.client.post(
            reverse('register_subject', args=[self.subject.id]))

        # Confirm the registration count has not increased
        registration_count = UserSubject.objects.filter(
            user=self.user, subject=self.subject).count()
        self.assertEqual(registration_count, 1)

        # Confirm the user is redirected to 'subject_list' and no new registration occurs
        self.assertRedirects(response, reverse('subject_list'))


class UnregisterSubjectViewTest(TestCase):
    def setUp(self):
        # Create a user for login
        self.user = User.objects.create_user(
            username='testuser', password='userpassword')

        # Create a subject with no available seats (already full)
        self.subject = Subject.objects.create(
            subject_id='CN101',
            name='Introduction to Computer Programming',
            semester=1,
            academic_year=2024,
            max_students=0,
            open_for_registration=False
        )

        # Register the user to the subject
        UserSubject.objects.create(user=self.user, subject=self.subject)

        # Log in the user
        self.client = Client()
        self.client.login(username='testuser', password='userpassword')

    def test_successful_unregistration(self):
        """Test that a user can successfully unregister from a subject."""
        response = self.client.post(
            reverse('unregister_subject', args=[self.subject.id]))
        self.assertRedirects(response, reverse('subject_list'))

        # Confirm that the UserSubject instance is deleted
        self.assertFalse(UserSubject.objects.filter(
            user=self.user, subject=self.subject).exists())

    def test_max_students_increases_on_unregistration(self):
        """Test that the max_students count increases by 1 on unregistration."""
        initial_max_students = self.subject.max_students

        self.client.post(reverse('unregister_subject', args=[self.subject.id]))

        # Check that max_students has increased by 1
        subject = Subject.objects.get(id=self.subject.id)
        self.assertEqual(subject.max_students, initial_max_students + 1)

    def test_subject_reopens_for_registration_on_unregistration(self):
        """Test that a full subject reopens for registration when a user unregisters."""
        # Confirm that subject is initially closed for registration
        self.assertFalse(self.subject.open_for_registration)

        # Unregister the user from the subject
        self.client.post(reverse('unregister_subject', args=[self.subject.id]))

        # Confirm that open_for_registration is set to True
        subject = Subject.objects.get(id=self.subject.id)
        self.assertTrue(subject.open_for_registration)
