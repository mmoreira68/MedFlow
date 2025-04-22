from django.shortcuts import render

from .models import SalaEquipamento

def visualizar_agendamentos(request):
    sala_equipamentos = SalaEquipamento \
                        .objects.select_related('sala', 'equipamento') \
                        .order_by('-sala__andar', 'sala__numero')
    
    return render(request, 'visualizar_agendamentos.html', {'sala_equipamentos': sala_equipamentos})
