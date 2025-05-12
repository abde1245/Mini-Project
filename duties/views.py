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
    user_courses = Course.objects.filter(taught_by_faculty=request.user)
    duties = Assignment.objects.filter(course__in=user_courses).select_related(
        'course', 
        'assigned_to',  # CORRECTED: Use the field name from your Assignment model
        'assigned_by'   # CORRECTED: Use the field name from your Assignment model
    ).order_by('-due_date')
    return render(request, 'duties/professor_duties.html', {'duties': duties})

@faculty_required
def duty_create_view(request):
    if request.method == 'POST':
        form = DutyForm(request.POST, user=request.user) # Passing user to form for filtering
        if form.is_valid():
            duty = form.save(commit=False)
            duty.assigned_by = request.user # CORRECTED: Use 'assigned_by' to match your Assignment model
            duty.save()
            messages.success(request, 'Duty created successfully.')
            return redirect('duties:professor_duties_list')
    else:
        form = DutyForm(user=request.user) # Pass user for GET request too
    return render(request, 'duties/create_edit_duty.html', {'form': form, 'title': 'Create New Duty'})

@faculty_required
def duty_update_view(request, pk):
    # Ensure professor can only edit duties for courses they teach AND they assigned
    # Or just course__taught_by_faculty=request.user if any faculty for that course can edit
    duty = get_object_or_404(Assignment, pk=pk, course__taught_by_faculty=request.user)
    
    if request.method == 'POST':
        form = DutyForm(request.POST, instance=duty, user=request.user)
        if form.is_valid():
            # assigned_by should already be set or not change unless you allow it in the form
            form.save()
            messages.success(request, 'Duty updated successfully.')
            return redirect('duties:professor_duties_list')
    else:
        form = DutyForm(instance=duty, user=request.user)
    return render(request, 'duties/create_edit_duty.html', {'form': form, 'title': 'Edit Duty'})

@faculty_required
def duty_delete_view(request, pk):
    duty = get_object_or_404(Assignment, pk=pk, course__taught_by_faculty=request.user)
    if request.method == 'POST': # Ensure your template uses a POST form for deletion
        duty.delete()
        messages.success(request, 'Duty deleted successfully.')
        return redirect('duties:professor_duties_list')
    # It's good practice to have a confirmation template for GET requests to delete views
    return render(request, 'duties/duty_confirm_delete.html', {'duty': duty})


class CourseDutyListView(LoginRequiredMixin, ListView): # Simpler for now
    model = Assignment
    template_name = 'duties/course_duties_list.html' # You'll need to create this template
    context_object_name = 'duties'

    def get_queryset(self):
        # Get the course object based on course_id from URL
        self.course = get_object_or_404(Course, pk=self.kwargs['course_id'])
        
        # Filter assignments for this specific course
        # And only for the logged-in faculty member if that's the requirement
        queryset = Assignment.objects.filter(
            course=self.course
            # Optional: if only the professor teaching this course should see its duties
            # assigned_by=self.request.user # Or course__taught_by_faculty=self.request.user
        ).select_related('assigned_to', 'assigned_by', 'course').order_by('due_date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course # Add the course object to the context
        # Check if the current user is the one who should be viewing these duties
        # For example, if the course is taught by the logged-in user (professor)
        # This is a basic check; faculty_required decorator handles broader access.
        if not (hasattr(self.request.user, 'role') and self.request.user.role.role_name == 'Faculty' and self.course.taught_by_faculty == self.request.user):
            # Handle unauthorized access, maybe raise Http404 or PermissionDenied
            # For now, this will just not filter by user, but you should add proper auth
            pass
        return context