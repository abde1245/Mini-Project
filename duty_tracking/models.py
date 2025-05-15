# duty_tracking/models.py
from django.db import models
from django.core.exceptions import ValidationError
from users.models import CustomUser
from duties.models import Assignment

class DutyCompletionLog(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pending Verification'
        COMPLETED = 'COMPLETED', 'Completed'
        PARTIALLY_COMPLETED = 'PARTIALLY_COMPLETED', 'Partially Completed'
        NOT_COMPLETED = 'NOT_COMPLETED', 'Not Completed'

    duty = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='completion_logs'
    )
    fulfilled_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='duties_fulfilled_logs',
        limit_choices_to={'role__name': 'TA'},
        verbose_name='Fulfilled By (TA)',
        null=True,          # <-- add this
        blank=True 
    )
    updated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='duties_updated_logs',
        verbose_name='Updated By',
        null=True,          # <-- add this
        blank=True 
    )
    completion_timestamp = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=50,
        choices=StatusChoices.choices,
        default=StatusChoices.COMPLETED,
        help_text="The completion status of the duty."
    )
    comments = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('duty', 'fulfilled_by')
        ordering = ['-completion_timestamp']

    def clean(self):
        super().clean()
        if self.duty and self.duty.assigned_to and self.fulfilled_by:
            if self.duty.assigned_to != self.fulfilled_by:
                raise ValidationError(
                    f"This duty was assigned to {self.duty.assigned_to.username}, "
                    f"but is being marked as fulfilled by {self.fulfilled_by.username}."
                )

    def save(self, *args, **kwargs):
        # updated_by should always be set by admin/save_model
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_status_display()} - '{self.duty.title}' by {self.fulfilled_by.username}"