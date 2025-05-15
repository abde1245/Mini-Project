# views.py placeholder
# ta_assignments/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from users.dashboard_views import admin_required
from .models import TACourseAssignment
from .forms import TACourseAssignmentForm
from django.utils import timezone

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
            try:
                assignment.save()
                messages.success(request, 'TA successfully assigned to course.')
                return redirect('ta_assignments:assign_ta_course_list')
            except Exception as e: # Catch potential db errors like unique constraint
                messages.error(request, f"Error assigning TA: {e}")
    else:
        form = TACourseAssignmentForm()
    return render(request, 'ta_assignments/ta_course_assignment_form.html', {'form': form, 'title': "Assign TA to Course"})

# Add update and delete views similar to courses if time permits.
# For delete, ensure it's POST based with a confirmation.