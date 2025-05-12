# users/urls.py
from django.urls import path, include
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # path('register/', views.register_view, name='register'), # If you implement it

    path('dashboard/', views.dashboard_dispatch_view, name='dashboard_dispatch'),
    path('dashboards/', include('users.dashboard_urls')), # Includes admin_dashboard, etc.
]