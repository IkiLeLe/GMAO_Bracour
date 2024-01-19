from django.shortcuts import render, redirect
from maintenance_plan.models import Lines
from .forms import SignupForm, LoginForm
from django.contrib.auth import logout, authenticate, login
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

            return redirect('account/login/')
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

