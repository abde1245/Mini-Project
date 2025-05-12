# ta_assignments/admin.py
from django.contrib import admin
from .models import TACourseAssignment, TAFacultyAssignment # Corrected import

@admin.register(TACourseAssignment)
class TACourseAssignmentAdmin(admin.ModelAdmin):
    list_display = ('ta', 'course', 'assigned_by', 'start_date', 'end_date')
    list_filter = ('course', 'ta', 'start_date')
    search_fields = ('ta__username', 'course__course_name')

@admin.register(TAFacultyAssignment)
class TAFacultyAssignmentAdmin(admin.ModelAdmin):
    list_display = ('ta', 'faculty', 'assigned_by', 'start_date', 'end_date')
    list_filter = ('faculty', 'ta', 'start_date')
    search_fields = ('ta__username', 'faculty__username')

# If you had the old style registration, remove it:
# admin.site.register(TA_Course_Assignment) # Example of what to remove if it exists