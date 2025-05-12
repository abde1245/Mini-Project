# duties/admin.py
from django.contrib import admin
from .models import Assignment

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'assigned_to', 'assigned_by', 'due_date', 'created_at', 'is_completed') # Add 'is_completed' if you included it
    list_filter = ('course', 'assigned_to', 'assigned_by', 'due_date', 'is_completed') # Add 'is_completed'
    search_fields = ('title', 'description', 'course__course_name', 'assigned_to__username', 'assigned_by__username')
    # For making 'assigned_by' read-only or auto-filled in admin (more advanced)
    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
    #     if not obj: # If creating a new assignment
    #         # Limit 'assigned_by' to the current user if they are faculty
    #         # This requires request.user to be available, which it is in admin
    #         if hasattr(request.user, 'role') and request.user.role.name == 'Faculty':
    #             form.base_fields['assigned_by'].initial = request.user
    #             form.base_fields['assigned_by'].widget = forms.HiddenInput() # Or make it readonly
    #         else: # If admin is creating, let them choose
    #             pass
    #     return form

    # If you want to auto-set assigned_by on save:
    # def save_model(self, request, obj, form, change):
    #     if not obj.pk: # If creating new
    #         obj.assigned_by = request.user # Or specific logic
    #     super().save_model(request, obj, form, change)