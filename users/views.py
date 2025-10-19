from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomerRegistrationForms
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect



# Create your views here.
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomerRegistrationForms(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to GWCL Complaints Tracker')
            return redirect('dashboard')
    else:
        form = CustomerRegistrationForms()

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None: # User is authenticated
                login(request, user)
                messages.success(request, f'Eelcome back {username}.')
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully')
    return redirect('public_dashboard')

def home_view(request):
    # Redirect to public dashboard
    return redirect('public_dashboard')


@login_required
def dashboard_view(request):
    return render(request, 'users/dashboard.html')


@login_required
def dashboard_view(request):
    # Redirect based on role
    if request.user.is_customer():
        return redirect('my_complaints')
    elif request.user.is_staff_member():
        return redirect('staff_dashboard')  # We'll create this later
    elif request.user.is_manager():
        return redirect('manager_dashboard')  # We'll create this later
    
    return render(request, 'users/dashboard.html')