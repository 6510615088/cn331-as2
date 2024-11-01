from django.test import TestCase, Client
from django.urls import reverse
from .models import Subject

class SubjectModelTest(TestCase):
    # Test for adding a subject to the model
    def test_subject_creation(self):
        subject = Subject.objects.create(
            subject_id='CN101',
            name='Introduction to Computer Programming',
            semester=1,
            academic_year=2024,
            max_students=2,
            open_for_registration=True
        )
        self.assertEqual(subject.name, 'Introduction to Computer Programming')

    # Test for a client can reach a homepage or not
    def test_homepage(self):
        c = Client()
        response = c.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        