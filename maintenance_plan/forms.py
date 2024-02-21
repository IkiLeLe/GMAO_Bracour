from django import forms
from .models import PreventiveTask, CleaningTask, LubrificationTask, Lines, Equipement

class MaintenanceScheduleFilterForm(forms.Form):
    line = forms.ModelChoiceField(queryset=Lines.objects.all(), required=False, empty_label="All Lines", label="Line")
    equipement = forms.ModelChoiceField(queryset=Equipement.objects.all(), required=False, empty_label="All Equipments", label="Equipement")

    # ... (autres champs)
    frequency_choices = PreventiveTask.FREQUENCY_CHOICES
    frequency = forms.MultipleChoiceField(choices=frequency_choices, required=False, widget=forms.CheckboxSelectMultiple, label="Frequency")

    def __init__(self, *args, task_model=None, **kwargs):
        super(MaintenanceScheduleFilterForm, self).__init__(*args, **kwargs)
        if 'line' in self.data:
            try:
                line_id = int(self.data.get('line'))
                self.fields['equipement'].queryset = Equipement.objects.filter(lineId=line_id)
            except (ValueError, TypeError):
                pass

        # Update frequency choices based on the task_model
        if task_model == CleaningTask:
            self.frequency.choices = CleaningTask.FREQUENCY_CHOICES
        elif task_model == LubrificationTask:
            self.frequency.choices = LubrificationTask.FREQUENCY_CHOICES
