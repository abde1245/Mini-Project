# models.py placeholder
from django.db import models
from users.models import CustomUser

class Course(models.Model):
    course_code = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=255)
    credits = models.IntegerField()
    ltp = models.CharField(max_length=20)
    taught_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role__name': 'Faculty'})

    def __str__(self):
        return self.course_name

class Enrollment(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role__name': 'Student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.CharField(max_length=50)
    academic_year = models.CharField(max_length=50)
    enrollment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course', 'semester', 'academic_year')
