# models.py placeholder
from django.db import models
from django.conf import settings
from duties.models import Assignment
from courses.models import Course

class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Notification for {self.recipient}: {self.message[:50]}..."

    class Meta:
        ordering = ['-created_at']
