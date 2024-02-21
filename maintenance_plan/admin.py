from django.http import HttpResponseBadRequest
from typing import Any
from django.urls import reverse
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


class LineFilter(admin.SimpleListFilter):
    title = 'Line'
    parameter_name = 'line'

    def lookups(self, request, model_admin):
        lines = Lines.objects.all()
        return [(line.name, line.name) for line in lines]

    def queryset(self, request, queryset):
        line_name = self.value()
        if line_name:
            return queryset.filter(part__equipement__lineId__name=line_name)
        return queryset

class EquipementFilter(admin.SimpleListFilter):
    title = 'Equipement'
    parameter_name = 'equipement'

    def lookups(self, request, model_admin):
        line_name = request.GET.get('line')  # Obtenir la valeur sélectionnée dans LineFilter
        equipements = Equipement.objects.filter(lineId__name=line_name) if line_name else Equipement.objects.all()
        return [(equipement.serial_number, equipement.name) for equipement in equipements]

    def queryset(self, request, queryset):
        equipement_serial_number = self.value()
        if equipement_serial_number:
            return queryset.filter(part__equipement__serial_number=equipement_serial_number)
        return queryset

    def value(self):
        # Réinitialise la valeur si LineFilter a été modifié
        if 'line' in self.used_parameters:
            return None
        return super().value()

class EquipementChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.serial_number}-{obj.name}'

class BaseAdminForm(forms.ModelForm):
    line = forms.ModelChoiceField(queryset=Lines.objects.all(), required=False, label='Line')
    equipement = forms.ModelChoiceField(queryset=Equipement.objects.all(), required=False)

    class Meta:
        model = None
        fields = '__all__'

class PreventiveTaskAdminForm(BaseAdminForm):
    class Meta(BaseAdminForm.Meta):
        model = PreventiveTask

class CleaningTaskAdminForm(BaseAdminForm):
    class Meta(BaseAdminForm.Meta):
        model = CleaningTask

class LubrificationTaskAdminForm(BaseAdminForm):
    class Meta(BaseAdminForm.Meta):
        model = LubrificationTask

class PreventiveTaskAdmin(admin.ModelAdmin):
    form = PreventiveTaskAdminForm
    model = PreventiveTask

    class Media:
        js = ('js/update_parts.js',)
    
    def equipement_serial_number(self, obj):
        return obj.part.equipement.name if obj.part else None

    equipement_serial_number.short_description = 'Equipement'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # Ajoutez les champs 'line' et 'equipement' au formulaire si nécessaire
        form.base_fields['line'] = forms.ModelChoiceField(queryset=Lines.objects.all(), required=False, label='Line')
        form.base_fields['equipement'] = forms.ModelChoiceField(queryset=Equipement.objects.all(), required=False)

        return form

    fieldsets = [
        ('Equipement', {'fields': ['line','equipement']}),
        ('Maintenance préventive', {'fields': ['part', 'image', 'operation', 'mode', 'frequency', 'component', 'location', 'criteria', 'description', 'level', 'duration']}),
    ]

    list_display = ('operation', 'part', 'equipement_serial_number')
    inlines = [ContributorsInline]
    list_filter = (LineFilter, EquipementFilter,)





class CleaningTaskAdmin(admin.ModelAdmin): 
    form = CleaningTaskAdminForm
    model = CleaningTask

    class Media:
        js = ('js/update_parts.js',)
    
    def equipement_serial_number(self, obj):
        return obj.part.equipement.name if obj.part else None

    equipement_serial_number.short_description = 'Equipement'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # Ajoutez les champs 'line' et 'equipement' au formulaire si nécessaire
        form.base_fields['line'] = forms.ModelChoiceField(queryset=Lines.objects.all(), required=False, label='Line')
        form.base_fields['equipement'] = forms.ModelChoiceField(queryset=Equipement.objects.all(), required=False)

        return form

    fieldsets = [
        ('Equipement', {'fields': ['line','equipement']}),
        ('Maintenance préventive', {'fields': ['part', 'image', 'operation', 'mode', 'frequency', 'component', 'location', 'aids', 'description', 'level', 'duration']}),
    ]

    list_display = ('operation', 'part', 'equipement_serial_number')
    inlines = [ContributorsInline]
    list_filter = (LineFilter, EquipementFilter,)

class LubrificationTaskAdmin(admin.ModelAdmin):
    form = LubrificationTaskAdminForm
    model = LubrificationTask

    class Media:
        js = ('js/update_parts.js',)
    
    def equipement_serial_number(self, obj):
        return obj.part.equipement.name if obj.part else None

    equipement_serial_number.short_description = 'Equipement'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # Ajoutez les champs 'line' et 'equipement' au formulaire si nécessaire
        form.base_fields['line'] = forms.ModelChoiceField(queryset=Lines.objects.all(), required=False, label='Line')
        form.base_fields['equipement'] = forms.ModelChoiceField(queryset=Equipement.objects.all(), required=False)

        return form

    fieldsets = [
        ('Equipement', {'fields': ['line','equipement']}),
        ('Maintenance préventive', {'fields': ['part', 'image', 'operation', 'mode', 'frequency', 'component', 'location', 'lubrificant', 'description', 'level', 'duration']}),
    ]

    list_display = ('operation', 'part', 'equipement_serial_number')
    inlines = [ContributorsInline]
    list_filter = (LineFilter, EquipementFilter,)
    

admin.site.register(Lines, LinesAdmin)
admin.site.register(PreventiveTask, PreventiveTaskAdmin)
admin.site.register(Equipement, EquipementAdmin)
admin.site.register(Contributor)
admin.site.register(CleaningTask, CleaningTaskAdmin)
admin.site.register(LubrificationTask, LubrificationTaskAdmin)

