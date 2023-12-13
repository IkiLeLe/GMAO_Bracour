from django import forms
from .models import MaintenanceSchedule, Lines, Equipement

class MaintenanceScheduleFilterForm(forms.Form):
    line = forms.ModelChoiceField(queryset=Lines.objects.all(), required=False, empty_label="All Lines")
    equipement = forms.ModelChoiceField(queryset=Equipement.objects.all(), required=False, empty_label="All Equipments")
    frequency = forms.MultipleChoiceField(choices=MaintenanceSchedule.FREQUENCY_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    intervention_type = forms.MultipleChoiceField(choices=MaintenanceSchedule.INTERVENTION_TYPE_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super(MaintenanceScheduleFilterForm, self).__init__(*args, **kwargs)
        if 'line' in self.data:
            try:
                line_id = int(self.data.get('line'))
                self.fields['equipement'].queryset = Equipement.objects.filter(lineId=line_id)
            except (ValueError, TypeError):
                pass


            
"""
class MaintenanceScheduleFilterForm(forms.Form):
    line_id = forms.ModelChoiceField(queryset=Lines.objects.all(), required=False, label='Line')
    frequency = forms.ChoiceField(choices=MaintenanceSchedule.FREQUENCY_CHOICES, required=False)
    intervention_type = forms.ChoiceField(choices=MaintenanceSchedule.INTERVENTION_TYPE_CHOICES, required=False)
    level = forms.IntegerField(required=False)
    equipment = forms.ModelChoiceField(queryset=Equipement.objects.all(), required=False)
    clear_filter = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput())
    
class MaintenanceScheduleFilterForm(forms.Form):
    line = forms.ModelChoiceField(queryset=Lines.objects.all(), required=False, empty_label="All Lines")
    equipement = forms.ModelChoiceField(queryset=Equipement.objects.all(), required=False, empty_label="All Equipments")
    frequency = forms.MultipleChoiceField(choices=MaintenanceSchedule.FREQUENCY_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    intervention_type = forms.MultipleChoiceField(choices=MaintenanceSchedule.INTERVENTION_TYPE_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super(MaintenanceScheduleFilterForm, self).__init__(*args, **kwargs)
        if 'line' in self.data:
            try:
                line_id = int(self.data.get('line'))
                self.fields['equipement'].queryset = Equipement.objects.filter(lineId=line_id)
            except (ValueError, TypeError):
                pass
            
"""