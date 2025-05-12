# models.py placeholder
from django.db import models
from users.models import CustomUser
from duties.models import Assignment
from courses.models import Course

class Alert(models.Model):
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    related_assignment = models.ForeignKey(Assignment, on_delete=models.SET_NULL, null=True, blank=True)
    related_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    alert_text = models.TextField()
    alert_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=[
        ('Sent', 'Sent'), ('Delivered', 'Delivered'), ('Read', 'Read'),
        ('Acknowledged', 'Acknowledged'), ('Failed', 'Failed')
    ], default='Sent')
    timestamp = models.DateTimeField(auto_now_add=True)
