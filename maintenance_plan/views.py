from django.shortcuts import render, get_object_or_404
from django.views import generic, View
from .forms import MaintenanceScheduleFilterForm
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from reportlab.pdfgen import canvas
import csv
from django_filters import rest_framework as filters
from django.shortcuts import get_object_or_404


from .models import Lines, Equipement, MaintenanceSchedule, Section, Contributor, Contributors
 
# Create your views here.
class LineView(generic.TemplateView):
    template_name = 'maintenance_plan/equiplist.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["Line_list"] = Lines.objects.all()
        context["Equipement_list"] = Equipement.objects.all()
        return context
    # Dans views.py


"""
class MaintenanceScheduleFilter(filters.FilterSet):
    line = filters.ModelChoiceFilter(field_name='section__equipement__lineId', queryset=Lines.objects.all())
    equipement = filters.ModelChoiceFilter(field_name='section__equipement', queryset=Equipement.objects.all())
    frequency = filters.MultipleChoiceFilter(field_name='frequency', choices=MaintenanceSchedule.FREQUENCY_CHOICES)
    intervention_type = filters.MultipleChoiceFilter(field_name='intervention_type', choices=MaintenanceSchedule.INTERVENTION_TYPE_CHOICES)

    class Meta:
        model = MaintenanceSchedule
        fields = ['line', 'equipement', 'frequency', 'intervention_type']

    def get_filtered_queryset(self):
        return self.qs
  """     

class MaintenanceScheduleFilter:
    @staticmethod
    def get_filtered_queryset(request):
        line_filter = request.GET.get('line')
        equipement_filter = request.GET.get('equipement')
        frequency_filter = request.GET.getlist('frequency')
        intervention_type_filter = request.GET.getlist('intervention_type')

        queryset = MaintenanceSchedule.objects.all()

        if line_filter:
            queryset = queryset.filter(section__equipement__lineId=line_filter)
        if equipement_filter:
            queryset = queryset.filter(section__equipement__serial_number=equipement_filter)
        if frequency_filter:
            queryset = queryset.filter(frequency__in=frequency_filter)
        if intervention_type_filter:
            queryset = queryset.filter(intervention_type__in=intervention_type_filter)

        return queryset


class TaskView(generic.ListView):
    template_name = 'maintenance_plan/task.html'
    model = MaintenanceSchedule
    context_object_name = 'task_list'
    
    def get_queryset(self):
        return MaintenanceScheduleFilter.get_filtered_queryset(self.request)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = MaintenanceScheduleFilterForm(self.request.GET)
        return context
    
    


class EquipementView(generic.DetailView):
    template_name = 'maintenance_plan/equipdetail.html'
    model = Equipement

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipement_instance = self.get_object()
        
        # Get sections related to the equipment
        context['section_data'] = Section.objects.filter(equipement=equipement_instance)
        
        # Get maintenance schedules related to the equipment
        context['maintenance_schedules'] = MaintenanceSchedule.objects.filter(section__equipement=equipement_instance)
        
        return context

    
class MaintenanceScheduleDetailView(generic.DetailView):
    model = MaintenanceSchedule
    template_name = 'maintenance_plan/taskdetail.html'
    context_object_name = 'schedule'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contributors'] = self.object.ison.all()
        return context

class ExportCSVView(generic.View):
    def get(self, request, *args, **kwargs):
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="maintenance_schedule.csv"'

        writer = csv.writer(response)
        writer.writerow(['Operation', 'Section', 'Equipement', 'Line', 'Frequency', 'Mode', 'Level', 'Intervention Type'])
        
        queryset = MaintenanceScheduleFilter.get_filtered_queryset(request)
        
        for item in queryset:
            writer.writerow([item.operation, item.section.section_name, item.section.equipement.serial_number,
                            item.section.equipement.lineId, item.get_frequency_display(), item.get_mode_display(),
                            item.level, item.get_intervention_type_display()])

        return response
    
    

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
            p.drawString(100, y_position - 105, f'Intervention Type: {item.get_intervention_type_display()}')

        p.showPage()
        p.save()

        return response
    

    




"""  
class EquipementView(generic.DetailView):
    model = Equipement
    template_name = 'maintenance_plan/equipdetail.html'
    context_object_name = 'equipement_list'
    
     def get_queryset(self):
        return MaintenanceSchedule.objects.all()
        
      def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #mschedule_instance = self.get_object()
        context['ison'] = self.object.ison.all()
        return context
      
def get_queryset(self):
        queryset = MaintenanceSchedule.objects.all()
        line_filter = self.request.GET.get('line_filter')
        equipement_filter = self.request.GET.get('equipement_filter')
        frequency_filter = self.request.GET.get('frequency_filter')
        intervention_type_filter = self.request.GET.get('intervention_type_filter')

        if line_filter:
            queryset = queryset.filter(section__equipement__lineId=line_filter)
        if equipement_filter:
            queryset = queryset.filter(section__equipement__serial_number=equipement_filter)
        if frequency_filter:
            queryset = queryset.filter(frequency=frequency_filter)
        if intervention_type_filter:
            queryset = queryset.filter(intervention_type=intervention_type_filter)

        return queryset
        
def get_queryset(self):
        line_filter = self.request.GET.get('line')
        equipement_filter = self.request.GET.get('equipement')
        frequency_filter = self.request.GET.getlist('frequency')
        intervention_type_filter = self.request.GET.getlist('intervention_type')

        queryset = MaintenanceSchedule.objects.all()

        if line_filter:
            queryset = queryset.filter(section__equipement__lineId=line_filter)
        if equipement_filter:
            queryset = queryset.filter(section__equipement__serial_number=equipement_filter)
        if frequency_filter:
            queryset = queryset.filter(frequency__in=frequency_filter)
        if intervention_type_filter:
            queryset = queryset.filter(intervention_type__in=intervention_type_filter)

        return queryset
filter_instance = MaintenanceScheduleFilter(request.GET, queryset=MaintenanceSchedule.objects.all())
        queryset = filter_instance.qs
        
        def get_queryset(self):
        filter_instance = MaintenanceScheduleFilter(self.request.GET, queryset=MaintenanceSchedule.objects.all())
        return filter_instance.qs

class EquipementView(generic.DetailView):
    template_name = 'maintenance_plan/equipdetail.html'
    model = Equipement
    #slug_field ='serial_number'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipement_instance = self.get_object()
        context['section_data'] = Section.objects.filter(equipement=equipement_instance)
        return context
"""