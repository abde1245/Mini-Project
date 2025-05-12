# duty_tracking/models.py
from django.db import models
from django.core.exceptions import ValidationError
from users.models import CustomUser  # Assuming this is your custom user model
from duties.models import Assignment # The Duty/Task model

class DutyCompletionLog(models.Model):

    # Define choices for the status field
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pending Verification' # If a professor needs to verify
        COMPLETED = 'COMPLETED', 'Completed'
        PARTIALLY_COMPLETED = 'PARTIALLY_COMPLETED', 'Partially Completed'
        NOT_COMPLETED = 'NOT_COMPLETED', 'Not Completed' # e.g. TA couldn't do it
        # Add other statuses as needed, e.g., 'IN_PROGRESS', 'CANCELLED'

    # Changed 'duty' from OneToOneField back to ForeignKey to allow multiple logs IF NEEDED,
    # or if the OneToOne was an error and you meant a TA can log one status per duty.
    # If a duty can only ever have ONE completion log entry, then OneToOneField is correct.
    # However, if a TA can update their status (e.g. from In Progress to Completed),
    # then you might either update the existing log or create new ones (less common for status).
    # For now, assuming OneToOne means "one log record per duty ever".
    # If you mean "one log per TA per duty", then OneToOne on 'duty' isn't right if 'duty' is the PK here.
    # Let's assume the intent was that a given Assignment (duty) has one log, by one TA.
    # If an Assignment can be completed by multiple TAs (if it was a shared task not individually assigned in Assignment model),
    # then the model structure would be different.
    # Based on your `unique_together` comments, it seems you want one log per TA per duty.
    # Let's adjust `duty` to be a ForeignKey and use `unique_together`.

    duty = models.ForeignKey( # Changed from OneToOneField
        Assignment,
        on_delete=models.CASCADE,
        related_name='completion_logs' # Pluralized as there can be multiple if unique_together is on (ta, duty)
    )
    completed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='duties_completed_logs', # Pluralized
        # Make sure 'role__role_name' is the correct path to your Role model's name field
        limit_choices_to={'role__role_name': 'Student'} # TAs are students
    )
    completion_timestamp = models.DateTimeField(auto_now_add=True) # When the log entry was created/last updated
    
    # Re-adding the status field
    status = models.CharField(
        max_length=50,
        choices=StatusChoices.choices,
        default=StatusChoices.COMPLETED, # Default to 'Completed' when a log is made
        help_text="The completion status of the duty."
    )
    
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        duty_title_str = self.duty.title if self.duty and hasattr(self.duty, 'title') else "N/A Duty"
        completed_by_str = self.completed_by.username if self.completed_by and hasattr(self.completed_by, 'username') else "N/A User"
        return f"{self.get_status_display()} - '{duty_title_str}' by {completed_by_str}"

    class Meta:
        verbose_name = "Duty Completion Log"
        verbose_name_plural = "Duty Completion Logs"
        ordering = ['-completion_timestamp']
        # Ensures a TA can only have one completion log entry per specific duty.
        unique_together = ('duty', 'completed_by')

    def clean(self):
        super().clean() # Call super's clean first
        # Validate that the person marking complete is the one assigned, if the duty has an assignee
        if self.duty and self.duty.assigned_to and self.duty.assigned_to != self.completed_by:
            assigned_to_username = self.duty.assigned_to.username # Assumes assigned_to is not null
            raise ValidationError(
                f"This duty was assigned to {assigned_to_username}, "
                f"but is being marked with status by {self.completed_by.username}."
            )
        # Add any other validation logic for the status field if needed
        # For example, certain status transitions might not be allowed.