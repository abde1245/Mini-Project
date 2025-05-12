# duty_tracking/urls.py
from django.urls import path
from . import views # Assuming your views are in duty_tracking/views.py

app_name = 'duty_tracking'  # For namespacing

urlpatterns = [
    path('', views.ta_assigned_duties_view, name='ta_assigned_duties'),
    path('mark-complete/<int:assignment_pk>/', views.mark_duty_complete_view, name='mark_duty_complete'),
    # Add other URLs here if you implement more views, like a history view
    # path('history/', views.ta_duty_history_view, name='ta_duty_history'),
]

# If you have NO URLs for this app YET, an empty list is the minimum:
# urlpatterns = []