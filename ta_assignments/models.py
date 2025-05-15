from django.db import models
from users.models import CustomUser # Make sure this path is correct for your project structure
from courses.models import Course   # Make sure this path is correct

class TACourseAssignment(models.Model):
    ta = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='ta_course_assignments', # More descriptive related_name
        limit_choices_to={'role__name': 'TA'}, # TAs are students
        verbose_name="TA (Student)"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='ta_assignments'
    )
    assigned_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL, # Avoid deleting assignment if admin user is deleted
        null=True, # Must be nullable if SET_NULL is used
        blank=True, # Allow to be blank in forms, will be auto-set in admin
        related_name='course_assignments_created', # More descriptive
        limit_choices_to= {'role__name': 'Faculty', 'role__name': 'Admin'}, # Only Admins can assign
        verbose_name="Assigned by (Admin)"
    )
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        unique_together = ('ta', 'course')
        verbose_name = "TA Course Assignment"
        verbose_name_plural = "TA Course Assignments"

    def __str__(self):
        ta_name = self.ta.username if self.ta else "N/A"
        course_name = self.course.course_name if self.course else "N/A" # Assuming Course model has course_name
        return f"TA {ta_name} for Course {course_name}"

class TAFacultyAssignment(models.Model):
    ta = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='ta_faculty_assignments', # More descriptive
        limit_choices_to={'role__name': 'TA'}, # TAs are students
        verbose_name="TA (Student)"
    )
    faculty = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='assigned_tas_to_faculty', # More descriptive
        limit_choices_to={'role__name': 'Faculty'}, # Target Faculty role
        verbose_name="Faculty"
    )
    assigned_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL, # Avoid deleting assignment if admin user is deleted
        null=True, # Must be nullable if SET_NULL is used
        blank=True, # Allow to be blank in forms, will be auto-set in admin
        related_name='faculty_assignments_created', # More descriptive
        limit_choices_to={'role__name': 'Admin'}, # Only Admins can assign
        verbose_name="Assigned by (Admin)"
    )
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        unique_together = ('ta', 'faculty')
        verbose_name = "TA Faculty Assignment"
        verbose_name_plural = "TA Faculty Assignments"

    def __str__(self):
        ta_name = self.ta.username if self.ta else "N/A"
        faculty_name = self.faculty.username if self.faculty else "N/A"
        return f"TA {ta_name} for Faculty {faculty_name}"