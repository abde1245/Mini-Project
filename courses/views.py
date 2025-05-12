# views.py placeholder
# courses/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from users.dashboard_views import admin_required # Your decorator
from .models import Course
from .forms import CourseForm

@admin_required
def course_list_view(request):
    courses = Course.objects.select_related('taught_by').all()
    return render(request, 'courses/course_list.html', {'courses': courses})

@admin_required
def course_create_view(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course created successfully.')
            return redirect('courses:course_list')
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {'form': form, 'title': 'Create Course'})

@admin_required
def course_update_view(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully.')
            return redirect('courses:course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/course_form.html', {'form': form, 'title': 'Update Course'})

@admin_required
def course_delete_view(request, pk): # Basic GET-based delete for speed, POST is safer
    course = get_object_or_404(Course, pk=pk)
    # For safety, use a confirmation page and POST request for actual deletion
    # This is a simplified version for speed:
    if request.method == 'POST': # Make sure your template uses a POST form for this
        course.delete()
        messages.success(request, 'Course deleted successfully.')
        return redirect('courses:course_list')
    return render(request, 'courses/course_confirm_delete.html', {'course': course})