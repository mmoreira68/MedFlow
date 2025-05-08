from django import forms
from .models import AgendamentoSala

class AgendamentoSalaForm(forms.ModelForm):
    class Meta:
        model = AgendamentoSala
        fields = ['profissional', 'sala', 'data_agendamento', 'horario_inicio']
        widgets = {
            'profissional': forms.Select(attrs={'class': 'form-select'}),
            'sala': forms.Select(attrs={'class': 'form-select'}),
            'data_agendamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'horario_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }
