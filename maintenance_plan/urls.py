from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.conf import settings 
from django.conf.urls.static import static

from . import views
 
app_name = 'maintenance_plan'
urlpatterns = [
    path('account/', include('account.urls')),
    path('', views.LineView.as_view(), name='line'),
    path('<str:pk>/detail/', views.EquipementView.as_view(), name='detail'),
    path('task/', views.TaskView.as_view(), name='task'),
    path('task/<str:task_type>/<int:task_id>/', views.TaskDetailView.as_view(), name='taskdetail'),
    path('export_csv/', views.ExportCSVView.as_view(), name='export_csv'),
    path('export_pdf/', views.ExportPDFView.as_view(), name='export_pdf'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)