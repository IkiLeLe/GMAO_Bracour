from collections.abc import Callable, Sequence
from typing import Any
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
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



class EquipementFilter(admin.SimpleListFilter):
    title = 'Equipement'
    parameter_name = 'equipement'

    def lookups(self, request, model_admin):
        equipements = Equipement.objects.all()
        return [(equipement.serial_number, equipement.name) for equipement in equipements]

    def queryset(self, request, queryset):
        equipement_serial_number = self.value()
        if equipement_serial_number:
            return queryset.filter(part__equipement__serial_number=equipement_serial_number)
        return queryset

class EquipementChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.serial_number}-{obj.name}'

class PartFilteredChoiceField(forms.ModelChoiceField):
    def filter_parts_by_equipement(self, equipement_serial_number):
        return Part.objects.filter(equipement__serial_number=equipement_serial_number)

class PreventiveTaskAdminForm(forms.ModelForm):
    equipement = EquipementChoiceField(queryset=Equipement.objects.all(), required=False)
    part = PartFilteredChoiceField(queryset=Part.objects.all(), required=False)

    class Meta:
        model = PreventiveTask
        fields = '__all__'

class PreventiveTaskAdmin(admin.ModelAdmin):
    form = PreventiveTaskAdminForm
    inlines = [ContributorsInline]
    list_filter = (EquipementFilter,)

    fieldsets = [
        ('Equipement', {'fields': ['equipement']}),
        ('Maintenance préventive', {'fields': ['part', 'operation', 'mode', 'frequency', 'component', 'location', 'criteria', 'description', 'level', 'duration']}),
    ]

    list_display = ('operation', 'part', 'equipement_serial_number')

    def equipement_serial_number(self, obj):
        return obj.part.equipement.name

    equipement_serial_number.short_description = 'Equipement'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # Filtrer dynamiquement la liste déroulante 'part' en fonction de 'equipement'
        equipement_field = form.base_fields.get('equipement')
        part_field = form.base_fields.get('part')

        if equipement_field and part_field:
            equipement_serial_number = None

            if request.method == 'POST':
                # Récupérer la valeur à partir de la requête POST
                equipement_serial_number = request.POST.get('equipement_serial_number')

            elif obj:
                # Récupérer la valeur à partir de l'objet existant
                equipement_serial_number = getattr(obj, 'equipement_serial_number', None)

            print(f"equipement_serial_number: {equipement_serial_number}")

            if equipement_serial_number:
                part_field.queryset = Part.objects.filter(equipement__serial_number=equipement_serial_number)
                print("done")
            else:
                part_field.queryset = Part.objects.none()
                print("not done")

        return form
'''