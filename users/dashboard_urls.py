# users/dashboard_urls.py
from django.urls import path
from . import dashboard_views # Import from the correct views file

urlpatterns = [
    path('admin/', dashboard_views.admin_dashboard_view, name='admin_dashboard'),
    path('professor/', dashboard_views.professor_dashboard_view, name='professor_dashboard'),
    path('ta/', dashboard_views.ta_dashboard_view, name='ta_dashboard'),
]