from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings # For MEDIA_URL in DEBUG mode
from django.conf.urls.static import static # For MEDIA_URL in DEBUG mode

admin.site.site_header = "Dashboard"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls', namespace='users')), # Login, logout, dashboard dispatch

    # App-specific URLs
    path('courses/', include('courses.urls', namespace='courses')),
    path('ta-assignments/', include('ta_assignments.urls', namespace='ta_assignments')),
    path('duties/', include('duties.urls', namespace='duties')),
    path('duty-tracking/', include('duty_tracking.urls', namespace='duty_tracking')),
    path('submissions/', include('student_submissions.urls', namespace='student_submissions')), # Renamed for clarity and added
    # path('notifications/', include('notifications.urls', namespace='notifications')), # Keep commented if not ready
    # path('reporting/', include('reporting.urls', namespace='reporting')), # Keep commented if not ready

    # Root URL redirect:
    # If user is authenticated, redirect to their dashboard dispatch.
    # Otherwise, redirect to the login page.
    path('', lambda request: redirect(
        'users:dashboard_dispatch' if request.user.is_authenticated else 'users:login',
        permanent=False
    )),
]

# Serve media files during development (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Optionally, serve static files this way too if `runserver` isn't handling them correctly,
    # though usually `runserver` with `DEBUG=True` does this automatically for static files.
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # Only if STATIC_ROOT is defined