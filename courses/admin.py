# courses/admin.py
from django.contrib import admin
from .models import Course, Enrollment # Also import Enrollment if you plan to register it
from ta_assignments.models import TACourseAssignment

class TAAssignmentInline(admin.TabularInline):
    model = TACourseAssignment
    extra = 1
    # You might want to specify which fields from TACourseAssignment appear in the inline:
    # fields = ('ta', 'start_date', 'end_date', 'assigned_by') # Example
    # fk_name = 'course' # Django usually infers this, but can be explicit

class CourseAdmin(admin.ModelAdmin):
    inlines = [TAAssignmentInline]
    list_display = ('course_name', 'course_code', 'taught_by', 'credits', 'ltp') # Using actual field names from your Course model
    list_filter = ('taught_by',) # Example filter
    search_fields = ('course_name', 'course_code') # Example search

# --- Manage Course Model ---
# Unregister the basic one if it was somehow registered before without CourseAdmin
try:
    admin.site.unregister(Course)
except admin.sites.NotRegistered:
    pass # It's fine if it wasn't registered yet
admin.site.register(Course, CourseAdmin)

# --- Manage Enrollment Model (Optional, but good to have) ---
@admin.register(Enrollment) # Alternative way to register
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'semester', 'academic_year', 'enrollment_date')
    list_filter = ('course', 'semester', 'academic_year', 'student')
    search_fields = ('student__username', 'course__course_name') # Search by student username or course name