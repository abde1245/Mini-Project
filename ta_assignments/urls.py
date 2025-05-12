# ta_assignments/urls.py
from django.urls import path
from . import views # Assuming your views are in ta_assignments/views.py

app_name = 'ta_assignments'  # For namespacing

urlpatterns = [
    path('', views.list_ta_course_assignments, name='assign_ta_course_list'),
    path('assign-course/', views.assign_ta_to_course_view, name='assign_ta_to_course'),
    # Add other URLs here if you implement update/delete for TA assignments
    # Example:
    # path('update-course-assignment/<int:pk>/', views.update_ta_course_assignment_view, name='update_ta_course_assignment'),
    # path('delete-course-assignment/<int:pk>/', views.delete_ta_course_assignment_view, name='delete_ta_course_assignment'),

    # If you also have TA_Faculty_Assignments and want URLs for them:
    # path('faculty/', views.list_ta_faculty_assignments, name='assign_ta_faculty_list'),
    # path('assign-faculty/', views.assign_ta_to_faculty_view, name='assign_ta_to_faculty'),
]

# If you have NO URLs for this app YET, an empty list is the minimum:
# urlpatterns = []