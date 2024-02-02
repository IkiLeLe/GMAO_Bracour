from django.conf import settings 
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

app_name = 'account'

urlpatterns = [
    path('', views.login_view, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('password_change/', views.password_change, name='password_change'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

