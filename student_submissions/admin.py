from django.contrib import admin
from django.utils import timezone
from .models import Submission
from courses.models import Course, Enrollment
from ta_assignments.models import TACourseAssignment
from users.models import CustomUser  # Adjust the import path if your CustomUser model is in a different app

class GradedStatusFilter(admin.SimpleListFilter):
    title = 'Grading Status'
    parameter_name = 'graded_status'

    def lookups(self, request, model_admin):
        return (
            ('graded', 'Graded'),
            ('not_graded', 'Not Graded'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'graded':
            return queryset.exclude(grade_value__isnull=True).exclude(grade_value__exact='')
        if self.value() == 'not_graded':
            return queryset.filter(grade_value__isnull=True) | queryset.filter(grade_value__exact='')
        return queryset

class RelevantStudentFilter(admin.SimpleListFilter):
    title = 'Student'
    parameter_name = 'student__username'

    def lookups(self, request, model_admin):
        user = request.user
        qs = model_admin.get_queryset(request)
        # Only show students relevant to the current user
        if hasattr(user, 'role') and user.role and user.role.name == 'Faculty':
            courses = Course.objects.filter(taught_by=user)
            students = CustomUser.objects.filter(
                submissions_made__assignment__course__in=courses
            ).distinct()
        elif hasattr(user, 'role') and user.role and user.role.name == 'TA':
            ta_courses = TACourseAssignment.objects.filter(ta=user).values_list('course', flat=True)
            students = CustomUser.objects.filter(
                submissions_made__assignment__course__in=ta_courses
            ).distinct()
        elif hasattr(user, 'role') and user.role and user.role.name == 'Student':
            students = CustomUser.objects.filter(pk=user.pk)
        else:  # Admin
            students = CustomUser.objects.all()
        return [(s.username, s.get_full_name() or s.username) for s in students]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(student__username=self.value())
        return queryset

class RelevantCourseFilter(admin.SimpleListFilter):
    title = 'Course code'
    parameter_name = 'assignment__course__course_code'

    def lookups(self, request, model_admin):
        user = request.user
        qs = model_admin.get_queryset(request)
        if hasattr(user, 'role') and user.role and user.role.name == 'Faculty':
            courses = Course.objects.filter(taught_by=user)
        elif hasattr(user, 'role') and user.role and user.role.name == 'TA':
            ta_courses = TACourseAssignment.objects.filter(ta=user).values_list('course', flat=True)
            courses = Course.objects.filter(pk__in=ta_courses)
        elif hasattr(user, 'role') and user.role and user.role.name == 'Student':
            enrolled_courses = Enrollment.objects.filter(student=user).values_list('course', flat=True)
            courses = Course.objects.filter(pk__in=enrolled_courses)
        else:  # Admin
            courses = Course.objects.all()
        return [(c.course_code, f"{c.course_code} - {c.course_name}") for c in courses]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(assignment__course__course_code=self.value())
        return queryset

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'assignment',
        'student',
        'submission_timestamp',
        'submission_file',
        'submission_type',
        'graded_by',
        'grade_value',
        'grading_timestamp'
    )
    list_filter = (
        'submission_type',
        RelevantCourseFilter,
        RelevantStudentFilter,
        GradedStatusFilter,
    )
    search_fields = (
        'student__username',
        'assignment__title',
        'submission_file'
    )
    raw_id_fields = ('assignment', 'student', 'graded_by')
    readonly_fields = ('submission_timestamp', 'grading_timestamp')

    def get_fieldsets(self, request, obj=None):
        user_role = getattr(getattr(request.user, 'role', None), 'name', '').lower()
        if user_role == 'student':
            return (
                ('Submission Details', {
                    'fields': ('assignment', 'submission_file', 'submission_type', 'submission_timestamp')
                }),
            )
        elif user_role in ('ta', 'faculty'):
            return (
                ('Submission Details', {
                    'fields': ('assignment', 'student', 'submission_file', 'submission_type', 'submission_timestamp')
                }),
                ('Grading Information', {
                    'fields': ('grade_value', 'comments')
                }),
            )
        # Otherwise, show all fields (for admin/superuser)
        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:
            readonly.extend(['assignment', 'student'])
        return readonly

    def save_model(self, request, obj, form, change):
        user_role = getattr(getattr(request.user, 'role', None), 'name', '').lower()
        if not obj.student_id:
            obj.student = request.user
        # Automatically set graded_by and grading_timestamp if grading fields are being set
        if user_role in ('ta', 'faculty'):
            if obj.grade_value is not None:
                obj.graded_by = request.user
                obj.grading_timestamp = timezone.now()
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user

        # Admins see all
        if user.is_superuser or (hasattr(user, 'role') and user.role and user.role.name == 'Admin'):
            return qs

        # Faculty: submissions for assignments in their courses
        if hasattr(user, 'role') and user.role and user.role.name == 'Faculty':
            courses = Course.objects.filter(taught_by=user)
            return qs.filter(assignment__course__in=courses)

        # TA: submissions for assignments in their TA courses
        if hasattr(user, 'role') and user.role and user.role.name == 'TA':
            ta_courses = TACourseAssignment.objects.filter(ta=user).values_list('course', flat=True)
            return qs.filter(assignment__course__in=ta_courses)

        # Student: only their own submissions
        if hasattr(user, 'role') and user.role and user.role.name == 'Student':
            return qs.filter(student=user)

        # Default: show nothing
        return qs.none()