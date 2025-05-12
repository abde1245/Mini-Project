# student_submissions/admin.py
from django.contrib import admin
from .models import Submission

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'assignment',
        'student',                 # CORRECTED from 'student_user'
        'submission_timestamp',
        'submission_type',
        'graded_by',               # CORRECTED from 'graded_by_ta_user'
        'grade_value'
    )
    # For list_filter, if 'assignment' has a 'course' ForeignKey, and 'course' has an 'id' or 'course_code'
    # 'assignment__course__id' or 'assignment__course__course_code' might be better.
    # 'assignment__course_id' assumes 'course_id' is a direct field on Assignment (which it is, as a FK).
    list_filter = ('submission_type', 'assignment__course', 'graded_by') # Updated filters for better use

    # For search_fields, if 'student' is a ForeignKey to CustomUser which has 'username'
    search_fields = (
        'student__username',       # CORRECTED: Use 'student__username'
        'assignment__title'
    )
    # It's good practice to add raw_id_fields for ForeignKeys to improve admin performance
    # if you have many assignments, students, or graders.
    raw_id_fields = ('assignment', 'student', 'graded_by')

# Ensure this admin.py is saved in the student_submissions app directory.