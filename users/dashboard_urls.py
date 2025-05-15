# users/dashboard_urls.py
from django.urls import path
from . import dashboard_views # Import views from dashboard_views.py

# This file is included by users/urls.py under the 'dashboards/' path

urlpatterns = [
    # These names should match the redirects in dashboard_dispatch_view
    path('admin/', dashboard_views.admin_dashboard_view, name='admin_dashboard'),
    path('professor/', dashboard_views.professor_dashboard_view, name='professor_dashboard'),
    path('ta/', dashboard_views.ta_dashboard_view, name='ta_dashboard'),
    #path('student/', dashboard_views.student_dashboard_view, name='Student_dashboard'), # This is for students (including TAs)
    # Optional: path('student/', dashboard_views.student_dashboard_view, name='student_dashboard'),
]