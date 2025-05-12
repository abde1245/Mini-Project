# models.py placeholder
from django.db import models
from users.models import CustomUser
from courses.models import Course

class TACourseAssignment(models.Model):
    ta = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ta_course', limit_choices_to={'role__name': 'Student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigner_course')
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        unique_together = ('ta', 'course', 'start_date')

    def __str__(self):
        return f"{self.ta.username} assigned to {self.course.name}"
    
class TAFacultyAssignment(models.Model):
    ta = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ta_faculty', limit_choices_to={'role__name': 'Student'})
    faculty = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='faculty_ta', limit_choices_to={'role__name': 'Faculty'})
    assigned_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigner_faculty')
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        unique_together = ('ta', 'faculty', 'start_date')
