from django.shortcuts import render, redirect
from maintenance_plan.models import Lines, MaintenanceSchedule
from .forms import SignupForm, LoginForm
from django.contrib.auth import logout
from django.views.decorators.cache import cache_control


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout_view(request):
    logout(request)
    referer = request.META.get('HTTP_REFERER')
    if referer and referer.startswith('/login'):
        return redirect('account:login')
    return redirect('account:login') 

def index(request):
    lines = Lines.objects.all
    

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

            return redirect('/login/')
    else:
        form = SignupForm()

    return render(request, 'account/signup.html', {
        'form': form
    })