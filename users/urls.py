# users/urls.py
from django.urls import path, include
from . import views # Import main views
# from . import dashboard_views # Not strictly needed here as dashboard_urls handles imports

app_name = 'users' # Make sure you have app_name set

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # path('register/', views.register_view, name='register'), # Uncomment if you implement a registration view

    # URL for dispatching to the correct dashboard
    path('dashboard/', views.dashboard_dispatch_view, name='dashboard_dispatch'),

    # Include dashboard-specific URLs
    path('dashboards/', include('users.dashboard_urls')), # Includes admin_dashboard, etc.
]