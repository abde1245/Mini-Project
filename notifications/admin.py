from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from .models import Notification

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'created_at', 'is_read', 'assignment', 'course')
    list_filter = ('is_read', 'created_at', 'course')
    search_fields = ('message', 'recipient__username', 'assignment__title', 'course__course_code')
    readonly_fields = ('created_at',) # Make created_at read-only in the form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user

        # Superusers and Admins can see all notifications
        if user.is_superuser or (hasattr(user, 'role') and user.role and user.role.name == 'Admin'):
            return qs

        # Other users only see notifications addressed to them
        return qs.filter(recipient=user)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Get the notification object
        notification = self.get_object(request, object_id)

        # Check if the user is NOT an admin and the notification is not already read
        user = request.user
        if not (user.is_superuser or (hasattr(user, 'role') and user.role and user.role.name == 'Admin')) and notification and not notification.is_read:
            notification.is_read = True
            notification.save()

        # Call the parent change_view to render the form
        return super().change_view(request, object_id, form_url, extra_context)


# Unregister the default Notification admin if it was registered directly
# from duties.admin import Notification # Assuming Notification was imported here
# if admin.site.is_registered(Notification):
#     admin.site.unregister(Notification)

# Register the Notification model with the custom NotificationAdmin
admin.site.register(Notification, NotificationAdmin)
