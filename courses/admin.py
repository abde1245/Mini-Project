# courses/admin.py
from django.contrib import admin
from django.forms import HiddenInput
from .models import Course, Enrollment
from ta_assignments.models import TACourseAssignment

class TAAssignmentInline(admin.TabularInline):
    model = TACourseAssignment
    extra = 1

class CourseAdmin(admin.ModelAdmin):
    inlines = [TAAssignmentInline]
    list_display = ('course_name', 'course_code', 'taught_by', 'credits', 'ltp')
    list_filter = ('taught_by',)
    search_fields = ('course_name', 'course_code')

try:
    admin.site.unregister(Course)
except admin.sites.NotRegistered:
    pass
admin.site.register(Course, CourseAdmin)

# --- Custom Course Filter ---
class RelevantCourseFilter(admin.SimpleListFilter):
    title = 'course'
    parameter_name = 'course'

    def lookups(self, request, model_admin):
        user = request.user
        role = getattr(user, 'role', None)
        role_name = getattr(role, 'name', None)
        if role_name == 'Faculty':
            courses = Course.objects.filter(taught_by=user)
        elif role_name == 'TA':
            ta_courses = TACourseAssignment.objects.filter(ta=user).values_list('course', flat=True)
            courses = Course.objects.filter(pk__in=ta_courses)
        else:
            courses = Course.objects.all()
        return [(c.pk, f"{c.course_code} - {c.course_name}") for c in courses]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(course__pk=self.value())
        return queryset

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'semester', 'academic_year', 'enrollment_date')
    list_filter = ('course', 'semester', 'academic_year', 'student')
    search_fields = ('student__username', 'course__course_name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        role = getattr(user, 'role', None)
        role_name = getattr(role, 'name', None)
        if role_name == 'Student':
            return qs.filter(student=user)
        elif role_name == 'Faculty':
            return qs.filter(course__taught_by=user)
        elif role_name == 'TA':
            ta_courses = TACourseAssignment.objects.filter(ta=user).values_list('course_id', flat=True)
            return qs.filter(course_id__in=ta_courses)
        return qs

    def get_list_filter(self, request):
        user = request.user
        role = getattr(user, 'role', None)
        role_name = getattr(role, 'name', None)
        if role_name == 'Student':
            return ()
        elif role_name in ('Faculty', 'TA'):
            # Only show relevant course filter, semester, and academic year
            return (RelevantCourseFilter, 'semester', 'academic_year')
        return self.list_filter

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        user = request.user
        role = getattr(user, 'role', None)
        role_name = getattr(role, 'name', None)
        if role_name == 'Student':
            if 'student' in form.base_fields:
                form.base_fields['student'].initial = user.pk
                form.base_fields['student'].widget = HiddenInput()
        return form

    def save_model(self, request, obj, form, change):
        user = request.user
        role = getattr(user, 'role', None)
        role_name = getattr(role, 'name', None)
        if role_name == 'Student':
            obj.student = user
        super().save_model(request, obj, form, change)