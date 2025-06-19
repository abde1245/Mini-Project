# duty_tracking/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from users.dashboard_views import student_required # TAs are students
from duties.models import Assignment
from .models import DutyCompletionLog
from .forms import MarkDutyCompleteForm
from django.utils import timezone
from django.db.models import Exists, OuterRef

#@student_required
def ta_assigned_duties_view(request):
    ta_user = request.user

    # Subquery to check if a completion log exists for the current user and assignment
    completion_log_exists = DutyCompletionLog.objects.filter(
        assignment=OuterRef('pk'),
        ta_user=ta_user
    )

    # Get all duties assigned to this TA, and annotate if completed by them
    all_assigned_duties = Assignment.objects.filter(
        assigned_to_ta_user=ta_user
    ).select_related('course', 'assigned_by_user__role').annotate(
        is_completed_by_me=Exists(completion_log_exists)
    ).order_by('due_date')

    pending_duties = all_assigned_duties.filter(is_completed_by_me=False, due_date__gte=timezone.now().date())
    completed_duties = all_assigned_duties.filter(is_completed_by_me=True)
    past_due_pending_duties = all_assigned_duties.filter(is_completed_by_me=False, due_date__lt=timezone.now().date())


    context = {
        'pending_duties': pending_duties,
        'completed_duties': completed_duties,
        'past_due_pending_duties': past_due_pending_duties,
        'current_time': timezone.now()
    }
    return render(request, 'duty_tracking/ta_assigned_duties.html', context)

#@student_required
def mark_duty_complete_view(request, assignment_pk):
    assignment = get_object_or_404(Assignment, pk=assignment_pk, assigned_to=request.user)
    if request.method == 'POST':
        form = MarkDutyCompleteForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.duty = assignment
            log.fulfilled_by = request.user
            log.updated_by = request.user
            log.save()
            print("log.status:", log.status, "COMPLETED:", DutyCompletionLog.StatusChoices.COMPLETED)  # Debug
            if log.status == DutyCompletionLog.StatusChoices.COMPLETED:
                assignment.is_completed = True
                assignment.save(update_fields=['is_completed'])
            else:
                assignment.is_completed = False
                assignment.save(update_fields=['is_completed'])
            messages.success(request, f"Duty '{assignment.title}' successfully marked as {log.status}.")
            return redirect('duty_tracking:ta_assigned_duties')
    else:
        # Use the internal value for initial status
        form = MarkDutyCompleteForm(initial={'status': DutyCompletionLog.StatusChoices.COMPLETED})
        
    return render(request, 'duty_tracking/mark_complete.html', {'form': form, 'assignment': assignment})