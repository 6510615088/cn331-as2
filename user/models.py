from django.conf import settings
from django.db import models
from subjectreg.models import Subject

class UserSubject(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'subject')

    def __str__(self):
        return f"{self.user.username} - {self.subject.name}"
