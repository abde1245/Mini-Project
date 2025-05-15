import os
from django.db import models
from django.utils import timezone
from users.models import CustomUser # Assuming users.models.CustomUser
from duties.models import Assignment  # Assuming duties.models.Assignment

def submission_upload_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/submissions/<assignment_id>/<student_username>/<filename>
    # Ensure assignment and student are set on the instance before saving the file
    assignment_id = instance.assignment.id if instance.assignment else 'unknown_assignment'
    student_username = instance.student.username if instance.student else 'unknown_student'
    # Sanitize filename to prevent directory traversal or other issues
    filename = os.path.basename(filename)
    return f'submissions/assignment_{assignment_id}/student_{student_username}/{filename}'

class Submission(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='submissions_made',
        limit_choices_to={'role__name': 'Student'} # Or 'TA' if TAs also submit for some reason
        # For submissions, any student (or TA if they also act as students for courses) can submit.
        # The key is that the logged-in user making the submission is a student for that course.
        # We can further validate in the form/view that the student is enrolled in the course of the assignment.
    )

    
    # submission_content = models.TextField(blank=True, null=True) # If you still want a text field for notes
    submission_file = models.FileField(
        upload_to=submission_upload_path,
        verbose_name="Submission File",
        null=True, # Allow submission without a file initially if you have other content types
        blank=True  # Or make it mandatory by removing null=True, blank=True
    )
    # file_type = models.CharField(max_length=100, blank=True) # Can be auto-populated or removed if not needed

    submission_timestamp = models.DateTimeField(default=timezone.now) # Use default=timezone.now for creation time

    SUBMISSION_TYPE_CHOICES = [
        ('INITIAL', 'Initial Submission'),
        ('RESUBMISSION', 'Resubmission'),
        ('LATE', 'Late Submission'),
        ('DRAFT', 'Draft'),
    ]
    submission_type = models.CharField(
        max_length=50,
        choices=SUBMISSION_TYPE_CHOICES,
        default='INITIAL', # A sensible default
        blank=True # If you want it to be optional or set programmatically
    )

    # Grading Fields
    graded_by = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='graded_submissions',
        # Limit who can be a grader
        limit_choices_to=models.Q(role__name='Faculty') | models.Q(role__name='TA')
    )
    grade_value = models.CharField(max_length=20, null=True, blank=True) # Increased length for flexibility
    grading_timestamp = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True, verbose_name="Grading Comments")

    def __str__(self):
        return f"Submission for '{self.assignment.title}' by {self.student.username}"

    def save(self, *args, **kwargs):
        if self.pk and self.submission_file: # if object exists and has a file
            try:
                old_instance = Submission.objects.get(pk=self.pk)
                if old_instance.submission_file and old_instance.submission_file != self.submission_file:
                    # Delete old file if a new one is uploaded
                    if os.path.isfile(old_instance.submission_file.path):
                        os.remove(old_instance.submission_file.path)
            except Submission.DoesNotExist:
                pass # New instance, no old file to delete
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the associated file when the submission record is deleted
        if self.submission_file:
            if os.path.isfile(self.submission_file.path):
                os.remove(self.submission_file.path)
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['-submission_timestamp']
        # A student might submit multiple times for an assignment (e.g. drafts, resubmissions)
        # If only one final submission is allowed, add:
        # unique_together = ('assignment', 'student') # If using submission_type to differentiate, remove this.