# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import UserLoginForm
from django.contrib import messages

def login_view(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard_dispatch')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('users:dashboard_dispatch')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('users:login')

@login_required
def dashboard_dispatch_view(request):
    user = request.user
    if hasattr(user, 'role') and user.role:
        # Use user.role.name instead of user.role.role_name
        if user.role.name == 'Admin':
            return redirect('users:admin_dashboard')
        elif user.role.name == 'Faculty':
            return redirect('users:professor_dashboard')
        elif user.role.name == 'Student': # TAs are Students
            return redirect('users:ta_dashboard')
        else:
            messages.warning(request, "Your role is not configured for a dashboard.")
            auth_logout(request)
            return redirect('users:login')
    else:
        messages.error(request, "User role not found. Please contact admin.")
        auth_logout(request)
        return redirect('users:login')