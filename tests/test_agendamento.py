import pytest
from datetime import date, time, timedelta
from django.core.exceptions import ValidationError
from medflow.forms import AgendamentoSalaForm
from medflow.models import AgendamentoSala

@pytest.mark.django_db
def test_form_agendamento_conflito(agendamento, sala, profissional):
    # Já existe agendamento 08:00–09:15 (pelos parâmetros do fixture)
    form = AgendamentoSalaForm(data={
        "profissional": profissional.id,
        "sala": sala.id,
        "data_agendamento": agendamento.data_agendamento,
        "horario_inicio": "08:30",
    })
    assert not form.is_valid()
    assert "Conflito de horário" in str(form.errors)

@pytest.mark.django_db
def test_form_agendamento_sem_parametros_reclama(sala, profissional):
    # Não cria o ProfissionalParametros
    form = AgendamentoSalaForm(data={
        "profissional": profissional.id,
        "sala": sala.id,
        "data_agendamento": "2025-01-02",
        "horario_inicio": "10:00",
    })
    assert not form.is_valid()
    assert "não possui parâmetros" in str(form.errors)
