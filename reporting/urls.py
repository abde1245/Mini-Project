# urls.py placeholder
# reporting/urls.py
app_name = 'reporting'

from django.urls import path
from . import views

urlpatterns = [
    path('ta-assignments/', views.ta_assignment_report, name='ta_assignment_report'),
    path('alerts/', views.alerts_view, name='alerts_view'),
]