from collections.abc import Callable, Sequence
from typing import Any
from django.contrib import admin
from django.http.request import HttpRequest

from .models import Lines, Equipement, MaintenanceSchedule, Section, Contributor, Contributors
# Register your models here.

    
class LinesAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Name', {'fields': ['name']}),
    ]
    
class SectionInline(admin.TabularInline):
    model = Section
    extra = 2
 
   
class EquipementAdmin(admin.ModelAdmin):
     fieldsets = [
        ('Name', {'fields': ['serial_number', 'name', 'lineId']}),
        ('Detail', {'fields': ['type', 'installation_date', 'manufacturer']}),
        ]
     inlines = [SectionInline]
     list_display = ('serial_number', 'name', 'lineId')
    
class ContributorsInline(admin.TabularInline):
    model = Contributors 
    extra = 3

class MaintenanceScheduleAdmin(admin.ModelAdmin): 
     
     def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'Section':
            kwargs['queryset'] = Section.objects.select_related('equipement')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
     
     def get_form(self, request, obj=None, **kwargs):
         form = super().get_form(request, obj, **kwargs)
         form.base_fields['section'].queryset = Section.objects.select_related('equipement')
         return form
      
     def equipement_serial_number(self, obj):
         return obj.section.equipement.name
         
     def get_fields(self, request, obj=None):
         fields = super().get_fields(request, obj)
         if obj:
             fields += ('equipement_serial_number')
         return fields
     
     equipement_serial_number.short_description = 'Equipement'
     list_display = ('operation','section', 'equipement_serial_number')
     
     fieldsets = [
         
        ('Description', {'fields': ['operation', 'description']}),
        ('Detail', {'fields': ['frequency', 'mode', 'level', 'type', 'duration', 'intervention_type', 'section']}),
        ]
     inlines = [ContributorsInline]
    

admin.site.register(Lines, LinesAdmin)
admin.site.register(MaintenanceSchedule, MaintenanceScheduleAdmin)
admin.site.register(Equipement, EquipementAdmin)
admin.site.register(Contributor)
