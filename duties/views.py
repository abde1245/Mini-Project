# duties/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from users.dashboard_views import faculty_required # Your decorator for faculty
from .models import Assignment
from courses.models import Course
from .forms import DutyForm
from django.views.generic import ListView # For the CourseDutyListView if you add it
from django.contrib.auth.mixins import LoginRequiredMixin # For CBVs
# from django.utils.decorators import method_decorator # If applying faculty_required to CBV dispatch

@faculty_required
def professor_duties_list_view(request):
    # Duties for courses taught by this professor
    # CORRECTED: Use 'taught_by' instead of 'taught_by_faculty'
    user_courses = Course.objects.filter(taught_by=request.user)
    duties = Assignment.objects.filter(course__in=user_courses).select_related(
        'course',
        'assigned_to',
        'assigned_by'
    ).order_by('-due_date')
    return render(request, 'duties/professor_duties.html', {'duties': duties})

@faculty_required
def duty_create_view(request):
    if request.method == 'POST':
        form = DutyForm(request.POST, user=request.user) # Passing user to form for filtering
        if form.is_valid():
            duty = form.save(commit=False)
            duty.assigned_by = request.user
            duty.save()
            messages.success(request, 'Duty created successfully.')
            return redirect('duties:professor_duties_list')
    else:
        form = DutyForm(user=request.user) # Pass user for GET request too
    # For duty_create_view
    return render(request, 'duties/create_duty.html', {'form': form, 'title': 'Create New Duty'})

@faculty_required
def duty_update_view(request, pk):
    # Ensure professor can only edit duties for courses they teach
    # CORRECTED: Use 'course__taught_by' instead of 'course__taught_by_faculty'
    duty = get_object_or_404(Assignment, pk=pk, course__taught_by=request.user)

    if request.method == 'POST':
        form = DutyForm(request.POST, instance=duty, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Duty updated successfully.')
            return redirect('duties:professor_duties_list')
    else:
        form = DutyForm(instance=duty, user=request.user)
    return render(request, 'duties/edit_duty.html', {'form': form, 'title': 'Edit Duty'})

@faculty_required
def duty_delete_view(request, pk):
    # CORRECTED: Use 'course__taught_by' instead of 'course__taught_by_faculty'
    duty = get_object_or_404(Assignment, pk=pk, course__taught_by=request.user)
    if request.method == 'POST':
        duty.delete()
        messages.success(request, 'Duty deleted successfully.')
        return redirect('duties:professor_duties_list')
    return render(request, 'duties/duty_confirm_delete.html', {'duty': duty})


class CourseDutyListView(LoginRequiredMixin, ListView):
    model = Assignment
    template_name = 'duties/course_duties_list.html'
    context_object_name = 'duties'

    def get_queryset(self):
        self.course = get_object_or_404(Course, pk=self.kwargs['course_id'])
        queryset = Assignment.objects.filter(
            course=self.course
            # Optional: Add filtering by user if needed here
            # assigned_by=self.request.user # If only duties assigned by the user
        ).select_related('assigned_to', 'assigned_by', 'course').order_by('due_date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        # Check if the current user is the one who should be viewing these duties
        # CORRECTED: Use 'taught_by' and 'role.name'
        is_faculty_for_course = (
            hasattr(self.request.user, 'role') and
            self.request.user.role is not None and # Check role is not None
            self.request.user.role.name == 'Faculty' and
            hasattr(self.course, 'taught_by') and # Check taught_by exists
            self.course.taught_by == self.request.user
        )
        if not is_faculty_for_course:
            # Decide how to handle unauthorized access, e.g., raise PermissionDenied
            # from django.core.exceptions import PermissionDenied
            # raise PermissionDenied("You are not authorized to view duties for this course.")
            # Or simply filter the queryset to be empty if they aren't the faculty
            # context['duties'] = Assignment.objects.none() # Example
            print(f"Warning: User {self.request.user} accessed duties for course {self.course.pk} but is not the assigned faculty.")
            pass # Current behavior allows view, add stricter check if needed
        return context