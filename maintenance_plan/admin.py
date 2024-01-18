from collections.abc import Callable, Sequence
from typing import Any
from django.contrib import admin
from django.http.request import HttpRequest
from django import forms
from .models import Lines, Equipement, Part, Contributor, Contributors, PreventiveTask, CleaningTask, LubrificationTask
# Register your models here.

    
class LinesAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Name', {'fields': ['name']}),
        ('Detail', {'fields': ['installation_date', 'target']}),
    ]
    
class PartInline(admin.TabularInline):
    model = Part
    extra = 2

 
class EquipementAdminForm(forms.ModelForm):
    class Meta:
        model = Equipement
        fields = '__all__'

class EquipementAdmin(admin.ModelAdmin):
    form = EquipementAdminForm
    fieldsets = [
        ('Name', {'fields': ['lineId', 'serial_number', 'name']}),
        ('Detail', {'fields': ['installation_date', 'manufacturer']}),

        ]
    inlines = [PartInline]
    list_display = ('serial_number', 'name', 'lineId')

    
        



    
class ContributorsInline(admin.TabularInline):
    model = Contributors 
    extra = 3
    fields = ['person', 'quantity']

class PreventiveTaskAdmin(admin.ModelAdmin): 
     def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'part':
            kwargs['queryset'] = Part.objects.select_related('equipement')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
     
     def get_form(self, request, obj=None, **kwargs):
         form = super().get_form(request, obj, **kwargs)
         form.base_fields['part'].queryset = Part.objects.select_related('equipement')
         return form
      
     def equipement_serial_number(self, obj):
         return obj.part.equipement.name
         
     def get_fields(self, request, obj=None):
         fields = super().get_fields(request, obj)
         if obj:
             fields += ('equipement_serial_number')
         return fields
     
     equipement_serial_number.short_description = 'Equipement'
     list_display = ('operation','part', 'equipement_serial_number')
     
     fieldsets = [
        ('Maintenance préventive', {'fields': ['part', 'operation', 'mode', 'frequency', 'component', 'location', 'criteria', 'description', 'level', 'duration']}),
        ]
     inlines = [ContributorsInline]
    
class CleaningTaskAdmin(admin.ModelAdmin): 
     def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'part':
            kwargs['queryset'] = Part.objects.select_related('equipement')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
     
     def get_form(self, request, obj=None, **kwargs):
         form = super().get_form(request, obj, **kwargs)
         form.base_fields['part'].queryset = Part.objects.select_related('equipement')
         return form
      
     def equipement_serial_number(self, obj):
         return obj.part.equipement.name
         
     def get_fields(self, request, obj=None):
         fields = super().get_fields(request, obj)
         if obj:
             fields += ('equipement_serial_number')
         return fields
     
     equipement_serial_number.short_description = 'Equipement'
     list_display = ('operation','part', 'equipement_serial_number')
     
     fieldsets = [
        ('Nettoyage', {'fields': ['part', 'operation', 'mode', 'frequency', 'component', 'location', 'aids', 'description', 'level', 'duration']}),
        ]
     inlines = [ContributorsInline]

class LubrificationTaskAdmin(admin.ModelAdmin):
     def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'part':
            kwargs['queryset'] = Part.objects.select_related('equipement')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
     
     def get_form(self, request, obj=None, **kwargs):
         form = super().get_form(request, obj, **kwargs)
         form.base_fields['part'].queryset = Part.objects.select_related('equipement')
         return form
      
     def equipement_serial_number(self, obj):
         return obj.part.equipement.name
         
     def get_fields(self, request, obj=None):
         fields = super().get_fields(request, obj)
         if obj:
             fields += ('equipement_serial_number')
         return fields
     
     equipement_serial_number.short_description = 'Equipement'
     list_display = ('operation','part', 'equipement_serial_number')
     
     fieldsets = [
        ('Lubrification', {'fields': ['part', 'operation', 'mode', 'frequency', 'component', 'location', 'lubrificant', 'quantity', 'description', 'level', 'duration']}),
        ]
     inlines = [ContributorsInline]

admin.site.register(Lines, LinesAdmin)
admin.site.register(PreventiveTask, PreventiveTaskAdmin)
admin.site.register(Equipement, EquipementAdmin)
admin.site.register(Contributor)
admin.site.register(CleaningTask, CleaningTaskAdmin)
admin.site.register(LubrificationTask, LubrificationTaskAdmin)
'''
class EquipementAdmin(admin.ModelAdmin):
     fieldsets = [
        ('Name', {'fields': ['lineId', 'serial_number', 'name']}),
        ('Detail', {'fields': ['installation_date', 'manufacturer']}),

        ]
     inlines = [PartInline, DocumentInline]
     list_display = ('serial_number', 'name', 'lineId')
'''