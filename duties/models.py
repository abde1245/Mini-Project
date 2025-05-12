# duties/models.py
from django.db import models
from users.models import CustomUser
from courses.models import Course

class Assignment(models.Model): # This represents a TA Duty/Task
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_duties")
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField()
    location = models.CharField(max_length=255, null=True, blank=True)
    weightage = models.FloatField(null=True, blank=True) # Or DecimalField for precision if it's currency/exact grades

    # Who the duty is assigned to (a TA)
    assigned_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_duties', # From TA's perspective: user.assigned_duties.all()
        limit_choices_to={'role__name__in': ['Student', 'TA']} # Assuming TAs have role 'Student' or 'TA'
    )

    # Who created the duty (a Faculty member)
    assigned_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE, # If faculty is deleted, their created duties are also deleted. Consider models.PROTECT or SET_NULL.
        related_name='created_duties', # From Faculty's perspective: user.created_duties.all()
        limit_choices_to={'role__name': 'Faculty'} # Ensure only faculty can create duties
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False) # You'll likely add this later, perhaps in duty_tracking or here

    def __str__(self):
        return f"{self.title} for {self.course.course_name}" # Assumes course_name on Course model

    class Meta:
        ordering = ['due_date'] # Example: order duties by due date by default