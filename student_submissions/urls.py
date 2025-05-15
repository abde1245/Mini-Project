from django.urls import path
from . import views

app_name = 'student_submissions'

urlpatterns = [
    path('submit/<int:assignment_id>/', views.create_submission, name='create_submission'),
    path('my-submissions/', views.my_submissions_list, name='my_submissions_list'),
    path('<int:pk>/', views.submission_detail_view, name='submission_detail'),
    path('<int:submission_id>/grade/', views.grade_submission_view, name='grade_submission'),
    # Add other URLs as needed, e.g., for listing all submissions for an assignment (for faculty/TAs)
]