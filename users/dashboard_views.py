# users/dashboard_views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
# from django.http import HttpResponseForbidden # Not currently used

# Role checking utility function
def role_required(role_name_to_check, login_url=None, message="You are not authorized to view this page."):
    """
    Decorator for views that checks that the logged-in user has a specific role.
    """
    actual_login_url = login_url or reverse_lazy('users:login')

    def decorator(view_func):
        @login_required(login_url=actual_login_url)
        def _wrapped_view(request, *args, **kwargs):
            # Ensure this line uses the correct attribute from your Role model
            if not (hasattr(request.user, 'role') and \
                    request.user.role and \
                    request.user.role.name == role_name_to_check): # CHANGED role_name to name, and parameter to role_name_to_check
                messages.error(request, message)
                if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role:
                    return redirect('users:dashboard_dispatch') 
                return redirect(actual_login_url)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# Specific role decorators using the utility function
admin_required = role_required('Admin')
faculty_required = role_required('Faculty')
student_required = role_required('Student') # TAs are students

@admin_required
def admin_dashboard_view(request):
    return render(request, 'admin_dashboard.html', {'message': "Admin Dashboard"})

@faculty_required
def professor_dashboard_view(request):
    return render(request, 'professor_dashboard.html', {'message': "Professor Dashboard"})

@student_required
def ta_dashboard_view(request):
    return render(request, 'ta_dashboard.html', {'message': "TA Dashboard"})