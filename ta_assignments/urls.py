# ta_assignments/urls.py
from django.urls import path
from . import views # Assuming your views are in ta_assignments/views.py

app_name = 'ta_assignments'  # For namespacing

urlpatterns = [
    path('', views.list_ta_course_assignments, name='assign_ta_course_list'),
    path('assign-course/', views.assign_ta_to_course_view, name='assign_ta_to_course'),
    path('ajax_get_courses/', views.ajax_get_courses, name='ajax_get_courses'),
]

# If you have NO URLs for this app YET, an empty list is the minimum:
# urlpatterns = []