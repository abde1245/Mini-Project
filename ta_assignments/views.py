# views.py placeholder
# ta_assignments/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from users.dashboard_views import admin_required
from .models import TACourseAssignment
from .forms import TACourseAssignmentForm
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from courses.models import Course
from .models import TAFacultyAssignment
from django.template.loader import render_to_string

@admin_required
def list_ta_course_assignments(request):
    assignments = TACourseAssignment.objects.select_related('ta', 'course', 'assigned_by_user').all()
    return render(request, 'ta_assignments/ta_course_assignment_list.html', {'assignments': assignments})

@admin_required
def assign_ta_to_course_view(request):
    if request.method == 'POST':
        form = TACourseAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            # Auto-set assigned_by to current admin user
            assignment.assigned_by = request.user
            assignment.save()
            messages.success(request, 'TA successfully assigned to course.')
            return redirect('ta_assignments:assign_ta_course_list')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # If it's an AJAX request, return the updated form HTML
            form_html = render_to_string('ta_assignments/ta_course_assignment_form.html', {'form': form, 'title': "Assign TA to Course"}, request=request)
            return JsonResponse({'form_html': form_html})
    else:
        form = TACourseAssignmentForm()

    return render(request, 'ta_assignments/ta_course_assignment_form.html', {'form': form, 'title': "Assign TA to Course"})

def ajax_get_courses(request):
    ta_id = request.GET.get('ta_id')
    if not ta_id:
        return JsonResponse({'success': False, 'message': 'TA not provided.'}, status=400)
    today = timezone.now().date()
    faculty_ids = TAFacultyAssignment.objects.filter(
        ta_id=ta_id,
        end_date__gte=today
    ).values_list('faculty', flat=True)
    courses = Course.objects.filter(taught_by__in=faculty_ids)
    course_list = [
        {'id': course.pk, 'text': f"{course.course_code} - {course.course_name}"}
        for course in courses
    ]
    return JsonResponse({'success': True, 'courses': course_list})

# Add update and delete views similar to courses if time permits.
# For delete, ensure it's POST based with a confirmation.