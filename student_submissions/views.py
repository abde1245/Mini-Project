from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseForbidden # For explicit forbidden access

from .models import Submission, Assignment # Assignment from duties.models
from .forms import StudentSubmissionForm, GradeSubmissionForm
from users.models import CustomUser # For role checking if needed

# Import your actual role decorators. Ensure 'ta_required' exists if you use it.
# If TAs are 'Student' role, use 'student_required' for them.
from users.dashboard_views import student_required, faculty_required, ta_required # Or just student_required if TAs are Students


# Helper function for combined role check (optional, but can simplify)
def faculty_or_ta_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if not (user.is_superuser or
                (hasattr(user, 'is_faculty') and user.is_faculty) or
                (hasattr(user, 'is_ta') and user.is_ta)):
            messages.error(request, "You are not authorized to perform this action.")
            return redirect('users:dashboard_dispatch') # Or appropriate redirect
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@student_required # Ensures only logged-in users with 'Student' (or 'TA' if they are students) role can access
def create_submission(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    user = request.user # This user is the student

    # More robust check: ensure student is enrolled in the assignment's course
    # Example (requires Enrollment model and logic):
    # from courses.models import Enrollment
    # if not Enrollment.objects.filter(student_user=user, course=assignment.course).exists():
    #     messages.error(request, "You are not enrolled in the course for this assignment.")
    #     return redirect('some_error_page_or_dashboard') # Redirect appropriately

    if request.method == 'POST':
        # Pass user for context if needed by form, assignment_instance to pre-fill/disable
        form = StudentSubmissionForm(request.POST, request.FILES, assignment_instance=assignment)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = user # Set student automatically
            submission.assignment = assignment # Ensure assignment is set
            submission.save()
            messages.success(request, f"Submission for '{assignment.title}' uploaded successfully.")
            return redirect('student_submissions:submission_detail', pk=submission.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StudentSubmissionForm(assignment_instance=assignment)

    context = {
        'form': form,
        'assignment': assignment,
        'title': f"Submit for: {assignment.title}"
    }
    return render(request, 'student_submissions/submission_form.html', context)


@login_required # Any logged-in user can try to access, further checks inside
def submission_detail_view(request, pk):
    submission = get_object_or_404(
        Submission.objects.select_related('student', 'assignment', 'assignment__course', 'graded_by'),
        pk=pk
    )
    user = request.user

    can_view = False
    is_grader_for_this = False

    if user.is_superuser:
        can_view = True
        is_grader_for_this = True # Superuser can grade anything
    elif user == submission.student:
        can_view = True
    elif hasattr(user, 'is_faculty') and user.is_faculty:
        if submission.assignment.course.taught_by_faculty == user:
            can_view = True
            is_grader_for_this = True
    elif hasattr(user, 'is_ta') and user.is_ta:
        # More specific TA check: is this TA assigned to this course?
        # from ta_assignments.models import TACourseAssignment
        # if TACourseAssignment.objects.filter(ta=user, course=submission.assignment.course).exists():
        #     can_view = True
        #     is_grader_for_this = True
        # Simplified: if a TA, they can view if they are *the* grader.
        # For broader TA view access, the above TACourseAssignment check is better.
        if submission.graded_by == user: # If they already graded it
            can_view = True
        # A TA might also be able to view (and subsequently grade) if assigned to the course.
        # This part needs alignment with how TA assignments are structured and checked.
        # For now, let's assume if they are a TA for the course, they can grade.
        # This is a placeholder for TA course assignment check:
        # if is_ta_for_course(user, submission.assignment.course):
        #    can_view = True
        #    is_grader_for_this = True


    if not can_view:
        messages.error(request, "You are not authorized to view this submission.")
        return redirect('users:dashboard_dispatch')

    context = {
        'submission': submission,
        'title': f"Submission Details: {submission.assignment.title}",
        'can_grade_submission': is_grader_for_this # Pass flag to template
    }
    return render(request, 'student_submissions/submission_detail.html', context)


@faculty_or_ta_required
def grade_submission_view(request, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id)
    user = request.user  # The grader

    if request.method == 'POST':
        form = GradeSubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            graded_submission = form.save(commit=False)
            graded_submission.graded_by = user  # Always set to current user
            graded_submission.grading_timestamp = timezone.now()  # Always set to now
            graded_submission.save()
            messages.success(request, "Submission graded successfully.")
            return redirect('student_submissions:submission_detail', pk=submission.id)
        else:
            messages.error(request, "Error grading submission. Please correct errors.")
    else:
        form = GradeSubmissionForm(instance=submission)

    context = {
        'form': form,
        'submission': submission,
        'title': f"Grade Submission: {submission.assignment.title} by {submission.student.username}"
    }
    return render(request, 'student_submissions/grade_submission_form.html', context)


@student_required # Or @login_required if any user can see their own. Student makes more sense.
def my_submissions_list(request):
    submissions = Submission.objects.filter(student=request.user).select_related(
        'assignment', 'assignment__course', 'graded_by'
    ).order_by('-submission_timestamp')
    context = {
        'submissions': submissions,
        'title': "My Submissions"
    }
    return render(request, 'student_submissions/my_submissions_list.html', context)