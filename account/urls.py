from django.conf import settings 
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

app_name = 'account'

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)