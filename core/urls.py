# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls', namespace='users')), # Login, logout, dashboard dispatch
    
    # App-specific URLs
    path('courses/', include('courses.urls', namespace='courses')),
    path('ta-assignments/', include('ta_assignments.urls', namespace='ta_assignments')),
    path('duties/', include('duties.urls', namespace='duties')),
    path('duty-tracking/', include('duty_tracking.urls', namespace='duty_tracking')),
    # path('student-submissions/', include('student_submissions.urls', namespace='student_submissions')), # Later
    # path('notifications/', include('notifications.urls', namespace='notifications')), # Later
    # path('reporting/', include('reporting.urls', namespace='reporting')), # Later

    # Root redirect
    path('', lambda request: redirect('users:login' if not request.user.is_authenticated else 'users:dashboard_dispatch', permanent=False)),
]