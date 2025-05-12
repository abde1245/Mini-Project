# admin.py placeholder
# duty_tracking/admin.py
from django.contrib import admin
from .models import DutyCompletionLog

@admin.register(DutyCompletionLog)
class DutyCompletionLogAdmin(admin.ModelAdmin):
    list_display = ('duty_title', 'completed_by_username', 'completion_timestamp', 'short_comments')
    list_filter = ('completion_timestamp', 'completed_by')
    search_fields = ('duty__title', 'completed_by__username', 'comments')
    readonly_fields = ('completion_timestamp',) # Usually set automatically

    def duty_title(self, obj):
        return obj.duty.title
    duty_title.short_description = 'Duty Title'
    duty_title.admin_order_field = 'duty__title' # Allows sorting

    def completed_by_username(self, obj):
        return obj.completed_by.username
    completed_by_username.short_description = 'Completed By'
    completed_by_username.admin_order_field = 'completed_by__username'

    def short_comments(self, obj):
        if obj.comments:
            return (obj.comments[:75] + '...') if len(obj.comments) > 75 else obj.comments
        return None
    short_comments.short_description = 'Comments'