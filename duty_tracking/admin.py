# admin.py placeholder
# duty_tracking/admin.py
from django.contrib import admin
from django import forms
from .models import DutyCompletionLog
from users.models import CustomUser
from ta_assignments.models import TAFacultyAssignment
from django.utils import timezone

class FulfilledByTAFilter(admin.SimpleListFilter):
    title = 'Fulfilled By (TA)'
    parameter_name = 'fulfilled_by'

    def lookups(self, request, model_admin):
        user = request.user
        # Admin: all TAs
        if user.is_superuser or (hasattr(user, 'role') and user.role and user.role.name == 'Admin'):
            tas = CustomUser.objects.filter(role__name='TA')
        # Faculty: only TAs assigned to them
        elif hasattr(user, 'role') and user.role and user.role.name == 'Faculty':
            ta_ids = TAFacultyAssignment.objects.filter(faculty=user).values_list('ta', flat=True)
            tas = CustomUser.objects.filter(pk__in=ta_ids)
        else:
            tas = CustomUser.objects.none()
        return [(ta.pk, ta.get_full_name() or ta.username) for ta in tas]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(fulfilled_by__pk=self.value())
        return queryset

@admin.register(DutyCompletionLog)
class DutyCompletionLogAdmin(admin.ModelAdmin):
    list_display = (
        'duty', 'status', 'fulfilled_by_username', 'updated_by', 'completion_timestamp', 'comments'
    )
    search_fields = ('duty__title', 'fulfilled_by__username', 'comments')
    list_filter = ('completion_timestamp', 'status')  # Default, will override below

    def get_readonly_fields(self, request, obj=None):
        # Make 'duty' field read-only when editing an existing entry
        if obj:  # This means the object already exists (editing)
            return ['duty'] + list(super().get_readonly_fields(request, obj))
        return super().get_readonly_fields(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        user = request.user

        # Hide fields for TA and Faculty
        if hasattr(user, 'role') and user.role:
            role = user.role.name
            if role == 'TA':
                from duties.models import Assignment
                from .models import DutyCompletionLog
                if not obj:  # Only filter duties when creating a new entry
                    completed_duties = DutyCompletionLog.objects.filter(
                        fulfilled_by=user, status='COMPLETED'
                    ).values_list('duty_id', flat=True)
                    form.base_fields['duty'].queryset = Assignment.objects.filter(
                        assigned_to=user,
                        is_completed=False
                    ).exclude(pk__in=completed_duties)
                # Hide fulfilled_by and updated_by fields
                form.base_fields.pop('fulfilled_by', None)
                form.base_fields.pop('updated_by', None)
            elif role == 'Faculty':
                from duties.models import Assignment
                from courses.models import Course
                courses = Course.objects.filter(taught_by=user)
                form.base_fields['duty'].queryset = Assignment.objects.filter(course__in=courses)
                ta_ids = TAFacultyAssignment.objects.filter(faculty=user).values_list('ta', flat=True)
                form.base_fields['fulfilled_by'].queryset = CustomUser.objects.filter(pk__in=ta_ids)
                form.base_fields.pop('updated_by', None)
        return form

    def save_model(self, request, obj, form, change):
        user = request.user
        if hasattr(user, 'role') and user.role:
            role = user.role.name
            if role == 'TA':
                obj.fulfilled_by = user
                obj.updated_by = user
            elif role == 'Faculty':
                obj.updated_by = user

        # Update the `is_completed` field in the related `Assignment` model
        if obj.status == 'COMPLETED':
            obj.duty.is_completed = True
            obj.duty.save(update_fields=['is_completed'])
        else:
            obj.duty.is_completed = False
            obj.duty.save(update_fields=['is_completed'])

        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """
        Filter the queryset based on the logged-in user's role.
        """
        qs = super().get_queryset(request)
        user = request.user

        if hasattr(user, 'role') and user.role:
            role = user.role.name
            if role == 'TA':
                # Show only entries fulfilled by the logged-in TA
                return qs.filter(fulfilled_by=user)
            elif role == 'Faculty':
                # Show only entries for TAs assigned to this faculty
                ta_ids = TAFacultyAssignment.objects.filter(faculty=user).values_list('ta', flat=True)
                return qs.filter(fulfilled_by__pk__in=ta_ids)
            elif role == 'Admin':
                # Admin sees all entries
                return qs
        # Default: return no entries if the role is not recognized
        return qs.none()

    def fulfilled_by_username(self, obj):
        # Returns the full name or username of the TA who fulfilled the duty
        if obj.fulfilled_by:
            return obj.fulfilled_by.get_full_name() or obj.fulfilled_by.username
        return "-"
    fulfilled_by_username.short_description = 'Fulfilled By (TA)'

    def delete_model(self, request, obj):
        """
        Override delete_model to update the is_completed field of the related Assignment.
        Only set is_completed=False if no other log for this assignment is marked as COMPLETED.
        """
        assignment = obj.duty
        super().delete_model(request, obj)
        # After deleting, check if any other logs for this assignment are still marked as COMPLETED
        if assignment and not assignment.completion_logs.filter(status='COMPLETED').exists():
            assignment.is_completed = False
            assignment.save(update_fields=['is_completed'])