from django.contrib.auth.decorators import login_required
from django.urls import path 
from django.conf import settings 
from django.conf.urls.static import static

from . import views
 
app_name = 'maintenance_plan'
urlpatterns = [
    path('', login_required(views.LineView.as_view()), name='line'),
    path('task/', login_required(views.TaskView.as_view()), name='task'),
    path('<str:pk>/detail/', login_required(views.EquipementView.as_view()), name='detail'),
    path('<int:pk>/taskdetail/', login_required(views.MaintenanceScheduleDetailView.as_view()), name='taskdetail'),
    path('export_csv/', login_required(views.ExportCSVView.as_view()), name='export_csv'),
    path('export_pdf/', login_required(views.ExportPDFView.as_view()), name='export_pdf'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)