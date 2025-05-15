# admin.py placeholder
# duty_tracking/admin.py
from django.contrib import admin
from django import forms
from .models import DutyCompletionLog

@admin.register(DutyCompletionLog)
class DutyCompletionLogAdmin(admin.ModelAdmin):
    list_display = (
        'duty_title',
        'status_display',
        'fulfilled_by_username',
        'updated_by_username',
        'completion_timestamp',
        'short_comments'
    )
    list_filter = ('completion_timestamp', 'fulfilled_by', 'status')
    search_fields = ('duty__title', 'fulfilled_by__username', 'comments')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Hide fulfilled_by for TAs (self-implied)
        if hasattr(request.user, 'role') and request.user.role and request.user.role.name == 'TA':
            if 'fulfilled_by' in form.base_fields:
                form.base_fields['fulfilled_by'].widget = forms.HiddenInput()
        # Make fulfilled_by readonly for faculty/admin
        elif hasattr(request.user, 'role') and request.user.role and request.user.role.name in ['Faculty', 'Admin']:
            if 'fulfilled_by' in form.base_fields:
                form.base_fields['fulfilled_by'].disabled = True
        # Hide updated_by for everyone (self-implied)
        if 'updated_by' in form.base_fields:
            form.base_fields['updated_by'].widget = forms.HiddenInput()
        # Hide completion_timestamp for everyone (auto)
        if 'completion_timestamp' in form.base_fields:
            form.base_fields['completion_timestamp'].widget = forms.HiddenInput()
        return form

    def save_model(self, request, obj, form, change):
        # Set fulfilled_by for TAs only on add
        if not change and hasattr(request.user, 'role') and request.user.role and request.user.role.name == 'TA':
            obj.fulfilled_by = request.user
        # Always set updated_by to the user making the change
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def status_display(self, obj):
        return obj.get_status_display()
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'

    def fulfilled_by_username(self, obj):
        return obj.fulfilled_by.username
    fulfilled_by_username.short_description = 'Fulfilled By'
    fulfilled_by_username.admin_order_field = 'fulfilled_by__username'

    def updated_by_username(self, obj):
        return obj.updated_by.username
    updated_by_username.short_description = 'Updated By'
    updated_by_username.admin_order_field = 'updated_by__username'

    def duty_title(self, obj):
        return obj.duty.title
    duty_title.short_description = 'Duty Title'
    duty_title.admin_order_field = 'duty__title'

    def short_comments(self, obj):
        if obj.comments:
            return (obj.comments[:75] + '...') if len(obj.comments) > 75 else obj.comments
        return None
    short_comments.short_description = 'Comments'