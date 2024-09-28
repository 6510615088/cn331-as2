from django.db import models

class Subject(models.Model):
    SEMESTER_CHOICES = [
        ('1', 'First Semester'),
        ('2', 'Second Semester'),
        ('3', 'Summer Semester'),
    ]
    
    subject_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES)
    academic_year = models.CharField(max_length=9)
    max_students = models.PositiveIntegerField()
    open_for_registration = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.subject_id} - {self.name}"

    