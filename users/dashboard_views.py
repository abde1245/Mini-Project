# users/dashboard_views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
# from django.http import HttpResponseForbidden # Not currently used
# Assuming CustomUser model is available via request.user

# Role checking utility function
def role_required(role_name_to_check, login_url=None, message="You are not authorized to view this page."):
    """
    Decorator for views that checks that the logged-in user has a specific role.
    """
    actual_login_url = login_url or reverse_lazy('users:login')

    def decorator(view_func):
        @login_required(login_url=actual_login_url)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            # Check if user has a role and if the role name matches
            # Uses the 'name' attribute of the Role model
            # Also checks if the user has the 'is_superuser' flag set, allowing superusers access to all role views (common practice)
            # Or you might want to restrict superusers to only the admin dashboard - adjust if needed.
            if not (user.is_superuser or (hasattr(user, 'role') and \
                    user.role is not None and \
                    user.role.name == role_name_to_check)):

                messages.error(request, message)

                # Redirect logic:
                # If user is authenticated and has a role, send them to their own dashboard
                if user.is_authenticated and hasattr(user, 'role') and user.role is not None:
                    # Avoid infinite redirect loops: if they are already trying to access
                    # dashboard_dispatch itself and fail the role check, redirect to login.
                     # This check is a bit tricky; redirecting to their *correct* dashboard is better.
                    # Let's redirect to the dispatcher, which will figure out the correct one.
                    return redirect('users:dashboard_dispatch')
                else:
                    # If not authenticated or role missing, redirect to login
                    return redirect(actual_login_url)

            # If role matches or is superuser, proceed to the view
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# Specific role decorators using the utility function
# Ensure the role names match exactly the 'name' field in your Role model instances ('Admin', 'Faculty', 'Student')
admin_required = role_required('Admin')
faculty_required = role_required('Faculty')
student_required = role_required('Student') # TAs are students
ta_required = role_required('TA')

@admin_required
def admin_dashboard_view(request):
    # Example: Fetch some data for the admin dashboard
    # from .models import CustomUser # Import model here if needed
    # total_users = CustomUser.objects.count()
    context = {
        'message': "Admin Dashboard",
        # 'total_users': total_users,
    }
    return render(request, 'admin_dashboard.html', context)

@faculty_required
def professor_dashboard_view(request):
    # Example: Fetch courses taught by this professor
    # from courses.models import Course # Import Course model
    # professor_courses = Course.objects.filter(taught_by_faculty=request.user)
    context = {
        'message': "Professor Dashboard",
        # 'professor_courses': professor_courses,
    }
    return render(request, 'professor_dashboard.html', context)

#@student_required
def ta_dashboard_view(request):
    # Example: Fetch duties assigned to this TA (who is a student)
    # from duties.models import Assignment # Import Assignment model
    # assigned_duties = Assignment.objects.filter(assigned_to_ta_user=request.user)
    context = {
        'message': "TA Dashboard",
        # 'assigned_duties': assigned_duties,
    }
    return render(request, 'ta_dashboard.html', context)


'''
@ta_required # <<< USE THE NEW DECORATOR if ta_dashboard_view is for users with 'TA' role
def ta_dashboard_view(request):
    # ...
    context = {'message': "TA Dashboard"}
    return render(request, 'ta_dashboard.html', context)

@student_required
def student_dashboard_view(request):
    context = {
        'message': "Student Dashboard",
        # 'assigned_duties': assigned_duties,
    }
    return render(request, 'student_dashboard.html', context)
'''