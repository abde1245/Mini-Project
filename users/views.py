# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import UserLoginForm # Keep this form import
# from .forms import UserRegistrationForm # Import if using registration view
from django.contrib import messages
# from .models import CustomUser # Import if needed in these views

def login_view(request):
    if request.user.is_authenticated:
        # Redirect authenticated users directly to the dashboard dispatcher
        return redirect('users:dashboard_dispatch')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Use Django's built-in login function
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            # Redirect to the dashboard dispatcher
            return redirect('users:dashboard_dispatch')
        else:
            # The form.errors will contain details, but a generic message is fine for login failure
            messages.error(request, "Invalid username or password.")
            # Optional: print(form.errors) for debugging login issues
    else:
        form = UserLoginForm()

    # Render the login page template with the form
    return render(request, 'users/login.html', {'form': form})

@login_required
def logout_view(request):
    """
    Logs out the user and redirects to the login page.
    """
    auth_logout(request)
    messages.info(request, "You have been successfully logged out.")
    # Redirect to the login page
    return redirect('users:login')

@login_required
def dashboard_dispatch_view(request):
    """
    Directs the logged-in user to the appropriate dashboard based on their role.
    """
    user = request.user # This user object will now have .is_admin, .is_faculty, .is_student

    # The properties on the user model will handle the logic
    if user.is_admin: # This will now work
        return redirect('users:admin_dashboard')
    elif user.is_faculty: # This will now work
        return redirect('users:professor_dashboard')
    elif user.is_ta or user.is_student: # <<< ADD THIS CONDITION
        return redirect('users:ta_dashboard')
    elif user.is_student: # This will now work
        # TAs are students, so they use the student dashboard
        return redirect('users:student_dashboard') # Or 'users:student_dashboard' if a general one exists
    else:
        # This case handles users who don't match any of the above roles,
        # or if 'role' is somehow None (though unlikely with current model setup).
        # The 'is_admin' property covers superusers, so they won't fall here unless
        # they also don't have the 'Admin' role and the other roles don't match.
        
        role_name_display = "Unknown/Not Set"
        if hasattr(user, 'role') and user.role:
            role_name_display = user.role.name

        messages.warning(request, f"Your role ('{role_name_display}') is not configured for a specific dashboard.")
        auth_logout(request) # Log out users with unhandled roles for safety
        return redirect('users:login')

# Example Registration View (currently not linked in urls.py)
"""
def register_view(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard_dispatch')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # You might want to automatically log the user in after registration
            # auth_login(request, user)
            messages.success(request, "Registration successful. Please log in.")
            return redirect('users:login')
        else:
            messages.error(request, "Registration failed. Please correct the errors.")
            # Form errors are available in the template: {{ form.errors }}
    else:
        form = UserRegistrationForm()

    # You'll need a template for registration: users/register.html
    return render(request, 'users/register.html', {'form': form})
"""