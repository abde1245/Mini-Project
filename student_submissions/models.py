# models.py placeholder
from django.db import models
from users.models import CustomUser
from duties.models import Assignment

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role__name': 'Student'})
    submission_timestamp = models.DateTimeField(auto_now_add=True)
    submission_content = models.TextField()
    file_type = models.CharField(max_length=100)
    submission_type = models.CharField(max_length=50)

    graded_by = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='graded_submissions')
    grade_value = models.CharField(max_length=10, null=True, blank=True)
    grading_timestamp = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
