from django.contrib import admin
from .models import TACourseAssignment, TAFacultyAssignment
from users.models import CustomUser # For type hinting or direct use if needed

class RelevantFacultyFilter(admin.SimpleListFilter):
    title = 'Faculty'
    parameter_name = 'faculty'

    def lookups(self, request, model_admin):
        user = request.user
        if user.is_superuser:
            faculties = CustomUser.objects.filter(role__name='Faculty')
        else:
            faculties = CustomUser.objects.filter(pk=user.pk, role__name='Faculty')
        return [(f.pk, f.get_full_name() or f.username) for f in faculties]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(faculty__pk=self.value())
        return queryset

class RelevantTAFilter(admin.SimpleListFilter):
    title = 'TA'
    parameter_name = 'ta'

    def lookups(self, request, model_admin):
        user = request.user
        if user.is_superuser:
            tas = CustomUser.objects.filter(role__name='TA')
        elif hasattr(user, 'role') and user.role and user.role.name == 'Faculty':
            # Only TAs assigned to this faculty
            tas = CustomUser.objects.filter(
                ta_faculty_assignments__faculty=user
            ).distinct()
        elif hasattr(user, 'role') and user.role and user.role.name == 'TA':
            tas = CustomUser.objects.filter(pk=user.pk)
        else:
            tas = CustomUser.objects.none()
        return [(ta.pk, ta.get_full_name() or ta.username) for ta in tas]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(ta__pk=self.value())
        return queryset

@admin.register(TACourseAssignment)
class TACourseAssignmentAdmin(admin.ModelAdmin):
    list_display = ('get_ta_display', 'get_course_display', 'get_assigned_by_display', 'start_date', 'end_date')
    list_filter = ('course__course_code', 'ta__username', 'start_date', 'assigned_by__username')
    search_fields = ('ta__username', 'ta__first_name', 'ta__last_name', 'course__course_name', 'course__course_code')
    
    # Use autocomplete fields for better UX with potentially many users/courses
    autocomplete_fields = ['ta', 'course', 'assigned_by']

    fieldsets = (
        (None, {
            'fields': ('ta', 'course', 'start_date', 'end_date')
        }),
        ('Assignment Meta', {
            'fields': ('assigned_by',),
            'classes': ('collapse',), # Keep it less prominent if auto-set
        }),
    )

    def get_ta_display(self, obj):
        return str(obj.ta)
    get_ta_display.short_description = 'TA (Student)'
    get_ta_display.admin_order_field = 'ta__username'

    def get_course_display(self, obj):
        return str(obj.course) # Relies on Course model's __str__
    get_course_display.short_description = 'Course'
    get_course_display.admin_order_field = 'course__course_name' # or course_code

    def get_assigned_by_display(self, obj):
        return str(obj.assigned_by) if obj.assigned_by else "N/A"
    get_assigned_by_display.short_description = 'Assigned By (Admin)'
    get_assigned_by_display.admin_order_field = 'assigned_by__username'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('assigned_by',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # If this is a new object being added
            obj.assigned_by = request.user
        super().save_model(request, obj, form, change)
    
    # The limit_choices_to on the model fields should handle dropdown filtering.
    # If autocomplete_fields are used, search_fields on related models (CustomUser, Course) are important.

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if user.is_superuser or (hasattr(user, 'role') and user.role and user.role.name == 'Admin'):
            return qs
        if hasattr(user, 'role') and user.role and user.role.name == 'Faculty':
            # Only show TA course assignments for this faculty's courses
            from courses.models import Course
            courses = Course.objects.filter(taught_by=user)
            return qs.filter(course__in=courses)
        if hasattr(user, 'role') and user.role and user.role.name == 'TA':
            return qs.filter(ta=user)
        return qs.none()

@admin.register(TAFacultyAssignment)
class TAFacultyAssignmentAdmin(admin.ModelAdmin):
    list_display = ('get_ta_display', 'get_faculty_display', 'get_assigned_by_display', 'start_date', 'end_date')
    list_filter = (RelevantFacultyFilter, RelevantTAFilter, 'start_date', 'end_date')
    search_fields = ('ta__username', 'ta__first_name', 'ta__last_name', 'faculty__username', 'faculty__first_name', 'faculty__last_name')
    autocomplete_fields = ['ta', 'faculty', 'assigned_by']

    fieldsets = (
        (None, {
            'fields': ('ta', 'faculty', 'start_date', 'end_date')
        }),
        ('Assignment Meta', {
            'fields': ('assigned_by',),
            'classes': ('collapse',),
        }),
    )

    def get_ta_display(self, obj):
        return str(obj.ta)
    get_ta_display.short_description = 'TA (Student)'
    get_ta_display.admin_order_field = 'ta__username'

    def get_faculty_display(self, obj):
        return str(obj.faculty)
    get_faculty_display.short_description = 'Faculty'
    get_faculty_display.admin_order_field = 'faculty__username'

    def get_assigned_by_display(self, obj):
        return str(obj.assigned_by) if obj.assigned_by else "N/A"
    get_assigned_by_display.short_description = 'Assigned By (Admin)'
    get_assigned_by_display.admin_order_field = 'assigned_by__username'

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('assigned_by',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # If this is a new object being added
            obj.assigned_by = request.user
        super().save_model(request, obj, form, change)