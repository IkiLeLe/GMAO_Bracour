from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import generic, View
from .forms import MaintenanceScheduleFilterForm
from django.http import JsonResponse, HttpResponse
from reportlab.pdfgen import canvas
import csv
from django_filters import rest_framework as filters




from .models import Lines, Equipement, PreventiveTask, CleaningTask, LubrificationTask, Part, Contributor, Contributors
 
# Create your views here.
@method_decorator(login_required, name='dispatch')
class LineView(generic.TemplateView):
    template_name = 'maintenance_plan/equiplist.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["Line_list"] = Lines.objects.all()
        context["Equipement_list"] = Equipement.objects.all()
        return context
    # Dans views.py

class MaintenanceScheduleFilter:
    @staticmethod
    def get_filtered_queryset(request, task_model=None):
        line_filter = request.GET.get('line')
        equipement_filter = request.GET.get('equipement')
        frequency_filter = request.GET.getlist('frequency')

        # Use the task_model to determine the appropriate model for the queryset
        if task_model is None:
            queryset = PreventiveTask.objects.all()
        elif task_model == CleaningTask:
            queryset = CleaningTask.objects.all()
        elif task_model == LubrificationTask:
            queryset = LubrificationTask.objects.all()
        else:
            raise ValueError("Invalid task_model specified")

        if line_filter:
            queryset = queryset.filter(part__equipement__lineId=line_filter)
        if equipement_filter:
            queryset = queryset.filter(part__equipement__serial_number=equipement_filter)
        if frequency_filter:
            queryset = queryset.filter(frequency__in=frequency_filter)

        return queryset


@method_decorator(login_required, name='dispatch')
class EquipementView(generic.DetailView):
    template_name = 'maintenance_plan/equipdetail.html'
    model = Equipement

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipement_instance = self.get_object()
        
        # Get sections related to the equipment
        context['section_data'] = Part.objects.filter(equipement=equipement_instance)
        
        # Get maintenance schedules related to the equipment
        context['maintenance_schedules'] = PreventiveTask.objects.filter(part__equipement=equipement_instance)
        
        return context

    
@method_decorator(login_required, name='dispatch')
class MaintenanceScheduleDetailView(generic.DetailView):
    model = PreventiveTask
    template_name = 'maintenance_plan/taskdetail.html'
    context_object_name = 'schedule'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contributors'] = self.object.ison.all()
        return context
    
@method_decorator(login_required, name='dispatch')
class TaskView(generic.ListView):
    template_name = 'maintenance_plan/task.html'
    context_object_name = 'task_list'

    def get_queryset(self):
        task_type = self.request.GET.get('type', 'preventive')
        if task_type == 'cleaning':
            return CleaningTask.objects.all()
        elif task_type == 'lubrification':
            return LubrificationTask.objects.all()
        else:
            return PreventiveTask.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = MaintenanceScheduleFilterForm(self.request.GET)
        context['cleaningtask_list'] = CleaningTask.objects.all()
        context['lubrificationtask_list'] = LubrificationTask.objects.all()
        return context

class ExportCSVView(generic.View):
    def get(self, request, *args, **kwargs):
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="maintenance_schedule.csv"'

        writer = csv.writer(response)
        writer.writerow(['Operation', 'Section', 'Equipement', 'Line', 'Frequency', 'Mode', 'Level'])
        
        queryset = MaintenanceScheduleFilter.get_filtered_queryset(request)
        
        for item in queryset:
            writer.writerow([item.operation, item.section.section_name, item.section.equipement.serial_number,
                            item.section.equipement.lineId, item.get_frequency_display(), item.get_mode_display(),
                            item.level])

        return response
    
@method_decorator(login_required, name='dispatch')
class ExportPDFView(generic.View):
    def get(self, request, *args, **kwargs):
       
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="maintenance_schedule.pdf"'

        p = canvas.Canvas(response)
        p.drawString(100, 800, 'Maintenance Schedule')
        
        queryset = MaintenanceScheduleFilter.get_filtered_queryset(request)

        y_position = 780
        for item in queryset:
            y_position -= 15
            p.drawString(100, y_position, f'Operation: {item.operation}')
            p.drawString(100, y_position - 15, f'Section: {item.section.section_name}')
            p.drawString(100, y_position - 30, f'Equipement: {item.section.equipement.serial_number}')
            p.drawString(100, y_position - 45, f'Line: {item.section.equipement.lineId}')
            p.drawString(100, y_position - 60, f'Frequency: {item.get_frequency_display()}')
            p.drawString(100, y_position - 75, f'Mode: {item.get_mode_display()}')
            p.drawString(100, y_position - 90, f'Level: {item.level}')
            

        p.showPage()
        p.save()

        return response
    

    




"""  
class TaskView(generic.ListView):
    template_name = 'maintenance_plan/task.html'
    model = PreventiveTask
    context_object_name = 'task_list'
    
    def get_queryset(self):
        return MaintenanceScheduleFilter.get_filtered_queryset(self.request)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = MaintenanceScheduleFilterForm(self.request.GET)
        return context
  """     