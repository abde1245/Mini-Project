# courses/urls.py
from django.urls import path
from . import views # Assuming you will have views in courses/views.py

app_name = 'courses'  # You should have added this for the namespace to work

urlpatterns = [
    path('', views.course_list_view, name='course_list'), # <--- ENSURE THIS PATTERN EXISTS AND IS NAMED 'course_list'
    path('create/', views.course_create_view, name='course_create'),
    path('update/<int:pk>/', views.course_update_view, name='course_update'),
    path('delete/<int:pk>/', views.course_delete_view, name='course_delete'),
]