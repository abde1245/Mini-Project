# duties/urls.py
from django.urls import path
from . import views

app_name = 'duties'

urlpatterns = [
    path('', views.professor_duties_list_view, name='professor_duties_list'),
    path('create/', views.duty_create_view, name='duty_create'),
    path('update/<int:pk>/', views.duty_update_view, name='duty_update'),
    path('delete/<int:pk>/', views.duty_delete_view, name='duty_delete'),

    # Make sure this line is commented out or removed if CourseDutyListView doesn't exist in views.py
    path('course/<int:course_id>/', views.CourseDutyListView.as_view(), name='course_duties'),
]