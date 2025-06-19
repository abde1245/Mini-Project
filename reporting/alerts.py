from datetime import timedelta
from django.utils import timezone
from ta_assignments.models import TACourseAssignment

def get_upcoming_assignment_expiry_alerts(days=7):
    today = timezone.now().date()
    soon = today + timedelta(days=days)
    expiring = TACourseAssignment.objects.filter(end_date__range=(today, soon))
    alerts = []
    for assignment in expiring:
        alerts.append(
            f"TA {assignment.ta} assignment for course {assignment.course} is expiring on {assignment.end_date}."
        )
    return alerts