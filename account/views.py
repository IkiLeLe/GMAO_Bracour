from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from maintenance_plan.models import Lines
from .forms import SignupForm, LoginForm, EditProfileForm
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import check_password
from django.views.decorators.cache import cache_control
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout_view(request):
    logout(request)
    if 'userToken' in request.session:
        del request.session['userToken']  # Remove the token from the session
    return redirect('account:login')


def index(request):
    lines = Lines.objects.all()
    return render(request, 'account/login.html', {
        'lines': lines,
    })
    
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.badge_number = form.cleaned_data['badge_number']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.position = form.cleaned_data['position']
            user.save()

            return redirect('account:login')
    else:
        form = SignupForm()

    return render(request, 'account/signup.html', {
        'form': form
    })


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Manually attempt to authenticate the user using the custom user model
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                request.session['userToken'] = 'valeur_du_token'
                return redirect('maintenance_plan:line')
            else:
                form.add_error(None, 'Invalid username or password')
                # The 'None' argument adds a non-field error to the form
        else:
            print("Form is invalid:", form.errors)  # Debugging statement
    else:
        form = LoginForm()

    return render(request, 'account/login.html', {'form': form})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            # Le formulaire est valide, enregistrer les modifications
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('account:edit_profile')
        else:
            messages.error(request, 'Error updating your profile. Please correct the errors below.')
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'account/edit_profile.html', {'form': form})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def password_change(request):
    if request.method == 'POST':
        password_form = PasswordChangeForm(user=request.user, data=request.POST)

        if password_form.is_valid():
            password_form.save()

            messages.success(request, 'Your password have been updated successfully.')
            return redirect('maintenance_plan:line')
        else:
            messages.error(request, 'Error updating your password. Please correct the errors below.')

    else:
        password_form = PasswordChangeForm(user=request.user)

    return render(request, 'account/edit_password.html', {'password_form': password_form})