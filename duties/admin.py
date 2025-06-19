# duties/admin.py
from django.contrib import admin
from django import forms
from .models import Assignment
from courses.models import Course, Enrollment
from users.models import CustomUser, Role
from ta_assignments.models import TACourseAssignment
from notifications.models import Notification
import json # Import json

class AssignmentAdminForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only set queryset if the field exists in the form
        if 'assigned_to' in self.fields:
            self.fields['assigned_to'].queryset = CustomUser.objects.filter(role__name='TA')

    class Media:
        js = ('js/assignment_ta_filter.js',)

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
    form = AssignmentAdminForm
    list_display = ('title', 'course', 'assigned_to', 'due_date', 'created_at', 'is_completed')
    search_fields = ('title', 'description', 'course__course_name', 'assigned_to__username')
    exclude = ('is_completed', 'assigned_by',)  # Remove from form

    def get_list_display(self, request):
        user = request.user
        if hasattr(user, 'role') and user.role and user.role.name == 'Student':
            # Hide 'assigned_to' for students
            return ('title', 'course', 'due_date', 'created_at')
        return self.list_display

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
            # Only show assignments assigned to this TA
            return qs.filter(assigned_to=user)
        if hasattr(user, 'role') and user.role and user.role.name == 'Student':
            enrolled_courses = Enrollment.objects.filter(student=user).values_list('course', flat=True)
            return qs.filter(course__in=enrolled_courses)
        return qs.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assigned_to":
            user = request.user
            if user.is_superuser or (hasattr(user, 'role') and user.role and user.role.name == 'Admin'):
                kwargs["queryset"] = CustomUser.objects.filter(role__name='TA')
            elif hasattr(user, 'role') and user.role and user.role.name == 'Faculty':
                # Only TAs assigned to this faculty's courses
                courses = Course.objects.filter(taught_by=user)
                ta_ids = TACourseAssignment.objects.filter(course__in=courses).values_list('ta', flat=True)
                kwargs["queryset"] = CustomUser.objects.filter(pk__in=ta_ids)
            elif hasattr(user, 'role') and user.role and user.role.name == 'TA':
                # TAs can only assign to themselves or other TAs in their courses if they have permission
                # Assuming TAs cannot change who an assignment is assigned *to* in the admin form.
                # If they could, the queryset should be restricted to TAs in courses they are assigned to.
                # For now, let's return an empty queryset for TAs to prevent selection.
                kwargs["queryset"] = CustomUser.objects.none()
            else:
                # Students shouldn't see this field or have choices
                kwargs["queryset"] = CustomUser.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # Set assigned_by on creation before saving the object
        if not obj.pk:
            obj.assigned_by = request.user

        # Save the assignment object first
        super().save_model(request, obj, form, change)

        # Now create notifications using the saved obj, only on creation
        if not change:
            # Create notification for the assigned TA
            if obj.assigned_to:
                Notification.objects.create(
                    recipient=obj.assigned_to,
                    message=f"You have been assigned a new duty: '{obj.title}' for course {obj.course.course_code}.",
                    assignment=obj,
                    course=obj.course
                )
            # Create notifications for students enrolled in the course
            enrolled_students = Enrollment.objects.filter(course=obj.course).select_related('student')
            for enrollment in enrolled_students:
                Notification.objects.create(
                    recipient=enrollment.student,
                    message=f"A new assignment '{obj.title}' has been posted for your course {obj.course.course_code}.",
                    assignment=obj,
                    course=obj.course
                )

        # Logic for Faculty notification on completion would need to be added where completion is marked.
        # If completion is marked via a custom action or view, the notification creation should go there.
        # If you were to add 'is_completed' back to the admin form and save it here, you could add logic like:
        # if change and 'is_completed' in form.changed_data and obj.is_completed:
        #     # Find the faculty teaching the course and create a notification
        #     if obj.course and obj.course.taught_by:
        #         Notification.objects.create(
        #             recipient=obj.course.taught_by,
        #             message=f"Assignment '{obj.title}' for course {obj.course.course_code} has been marked as completed by {obj.assigned_to.get_full_name() or obj.assigned_to.username}.",
        #             assignment=obj,
        #             course=obj.course
        #         )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        from ta_assignments.models import TACourseAssignment
        from users.models import CustomUser
        import json

        course_ta_map = {}
        user = request.user

        # Filter courses based on user role for the TA mapping
        if user.is_superuser or (hasattr(user, 'role') and user.role and user.role.name == 'Admin'):
            courses = Course.objects.all()
        elif hasattr(user, 'role') and user.role and user.role.name == 'Faculty':
            courses = Course.objects.filter(taught_by=user)
        elif hasattr(user, 'role') and user.role and user.role.name == 'TA':
            # TAs should only see TAs in courses they are assigned to
            ta_courses = TACourseAssignment.objects.filter(ta=user).values_list('course', flat=True)
            courses = Course.objects.filter(pk__in=ta_courses)
        else:
            courses = Course.objects.none() # Students shouldn't typically add/change assignments

        # Build the map only for relevant courses
        for course in courses:
            # Filter TAs based on the course
            ta_ids = TACourseAssignment.objects.filter(course=course).values_list('ta', flat=True)
            course_ta_map[course.pk] = list(ta_ids)

        # Check if 'assigned_to' field exists in the form before accessing its widget
        if 'assigned_to' in form.base_fields:
            form.base_fields['assigned_to'].widget.attrs['data-course-ta-map'] = json.dumps(course_ta_map)
        # If 'assigned_to' is not in base_fields (e.g., for a user role that cannot edit it),
        # we simply skip adding the data attribute.

        return form

#admin.site.register(Notification) # Ensure this is commented out or removed if registered in notifications/admin.py