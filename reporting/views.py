import csv
from django.http import HttpResponse
from django.shortcuts import render
from ta_assignments.models import TACourseAssignment
from .alerts import get_upcoming_assignment_expiry_alerts

def ta_assignment_report(request):
    # Only allow staff
    if not request.user.is_staff:
        return HttpResponse("Unauthorized", status=401)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ta_course_assignments.csv"'

    writer = csv.writer(response)
    writer.writerow(['TA', 'Course', 'Faculty', 'Start Date', 'End Date', 'Assigned By'])

    for assignment in TACourseAssignment.objects.select_related('ta', 'course', 'assigned_by'):
        writer.writerow([
            assignment.ta.get_full_name() if hasattr(assignment.ta, 'get_full_name') else str(assignment.ta),
            assignment.course.course_name if assignment.course else '',
            assignment.course.taught_by.get_full_name() if assignment.course and assignment.course.taught_by else '',
            assignment.start_date,
            assignment.end_date,
            assignment.assigned_by.get_full_name() if assignment.assigned_by else '',
        ])
    return response

def alerts_view(request):
    alerts = get_upcoming_assignment_expiry_alerts()
    return render(request, 'reporting/alerts.html', {'alerts': alerts})
