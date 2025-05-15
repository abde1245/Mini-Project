# duties/admin.py
from django.contrib import admin
from .models import Assignment
from courses.models import Course, Enrollment
from users.models import CustomUser, Role
from ta_assignments.models import TACourseAssignment

class RelevantCourseFilter(admin.SimpleListFilter):
    title = 'Course'
    parameter_name = 'course'

    def lookups(self, request, model_admin):
        user = request.user
        if user.is_superuser or (hasattr(user, 'role') and user.role and user.role.name == 'Admin'):
            courses = Course.objects.all()
        elif hasattr(user, 'role') and user.role and user.role.name == 'Faculty':
            courses = Course.objects.filter(taught_by=user)
        elif hasattr(user, 'role') and user.role and user.role.name == 'TA':
            ta_courses = TACourseAssignment.objects.filter(ta=user).values_list('course', flat=True)
            courses = Course.objects.filter(pk__in=ta_courses)
        elif hasattr(user, 'role') and user.role and user.role.name == 'Student':
            enrolled_courses = Enrollment.objects.filter(student=user).values_list('course', flat=True)
            courses = Course.objects.filter(pk__in=enrolled_courses)
        else:
            courses = Course.objects.none()
        return [(c.pk, f"{c.course_code} - {c.course_name}") for c in courses]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(course__pk=self.value())
        return queryset

class RelevantAssignedToFilter(admin.SimpleListFilter):
    title = 'Assigned to'
    parameter_name = 'assigned_to'

    def lookups(self, request, model_admin):
        user = request.user
        if user.is_superuser or (hasattr(user, 'role') and user.role and user.role.name == 'Admin'):
            tas = CustomUser.objects.filter(role__name='TA')
        elif hasattr(user, 'role') and user.role and user.role.name == 'Faculty':
            # Only TAs assigned to this faculty's courses
            courses = Course.objects.filter(taught_by=user)
            ta_ids = TACourseAssignment.objects.filter(course__in=courses).values_list('ta', flat=True)
            tas = CustomUser.objects.filter(pk__in=ta_ids)
        else:
            return []
        return [(ta.pk, ta.get_full_name() or ta.username) for ta in tas]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(assigned_to__pk=self.value())
        return queryset

class RelevantAssignedByFilter(admin.SimpleListFilter):
    title = 'Assigned by'
    parameter_name = 'assigned_by'

    def lookups(self, request, model_admin):
        user = request.user
        if user.is_superuser or (hasattr(user, 'role') and user.role and user.role.name == 'Admin'):
            faculty = CustomUser.objects.filter(role__name='Faculty')
            return [(f.pk, f.get_full_name() or f.username) for f in faculty]
        return []

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(assigned_by__pk=self.value())
        return queryset

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'assigned_to', 'due_date', 'created_at', 'is_completed')
    search_fields = ('title', 'description', 'course__course_name', 'assigned_to__username')
    exclude = ('is_completed', 'assigned_by',)  # Remove from form

    def get_list_filter(self, request):
        user = request.user
        filters = [RelevantCourseFilter]
        if user.is_superuser or (hasattr(user, 'role') and user.role and user.role.name == 'Admin'):
            filters.append(RelevantAssignedToFilter)
            filters.append(RelevantAssignedByFilter)
        elif hasattr(user, 'role') and user.role and user.role.name == 'Faculty':
            filters.append(RelevantAssignedToFilter)
        return filters

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if user.is_superuser or (hasattr(user, 'role') and user.role and user.role.name == 'Admin'):
            return qs
        if hasattr(user, 'role') and user.role and user.role.name == 'Faculty':
            courses = Course.objects.filter(taught_by=user)
            return qs.filter(course__in=courses)
        if hasattr(user, 'role') and user.role and user.role.name == 'TA':
            ta_courses = TACourseAssignment.objects.filter(ta=user).values_list('course', flat=True)
            return qs.filter(course__in=ta_courses)
        if hasattr(user, 'role') and user.role and user.role.name == 'Student':
            enrolled_courses = Enrollment.objects.filter(student=user).values_list('course', flat=True)
            return qs.filter(course__in=enrolled_courses)
        return qs.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assigned_to":
            kwargs["queryset"] = CustomUser.objects.filter(role__name='TA')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only set on creation
            obj.assigned_by = request.user
        super().save_model(request, obj, form, change)