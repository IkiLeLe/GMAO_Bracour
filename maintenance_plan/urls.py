from django.urls import path, include
from django.conf import settings 
from django.conf.urls.static import static



from . import views
 
app_name = 'maintenance_plan'
urlpatterns = [
    path('account/', include('account.urls')),
    path('', views.LineView.as_view(), name='line'),
    path('detail/<str:pk>/', views.EquipementView.as_view(), name='detail'),
    path('task/', views.TaskView.as_view(), name='task'),
    path('task/<str:task_type>/<int:task_id>/', views.TaskDetailView.as_view(), name='taskdetail'),
    path('export_csv/', views.ExportCSVView.as_view(), name='export_csv'),
    path('export_pdf/', views.ExportPDFView.as_view(), name='export_pdf'),
    path('part/<str:equipement_serial_number>/', views.PartFilterView.as_view(), name='part_filter_view'),
    path('equipement/<str:line_id>/', views.EquipementFilterView.as_view(), name='equipement_filter_view'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
