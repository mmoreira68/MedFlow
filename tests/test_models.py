import pytest
from django.db import IntegrityError
from medflow.models import Andar, Equipamento, Profissional, Sala, AgendamentoSala

@pytest.mark.django_db
def test_andar_nome_normalizado_unico():
    Andar.objects.create(nome="Térreo")
    with pytest.raises(IntegrityError):
        Andar.objects.create(nome="Terreo")  # deve colidir pelo nome_norm único

@pytest.mark.django_db
def test_equipamento_nome_normalizado_unico():
    Equipamento.objects.create(nome="Ultrassom")
    with pytest.raises(IntegrityError):
        Equipamento.objects.create(nome="Ultrássom")  # colide pelo nome_norm

@pytest.mark.django_db
def test_profissional_crm_unico():
    Profissional.objects.create(nome="Med 1", especialidade="Cardio", crm="ABC123")
    with pytest.raises(IntegrityError):
        Profissional.objects.create(nome="Med 2", especialidade="Cardio", crm="ABC123")

@pytest.mark.django_db
def test_agendamento_calcula_horario_final(agendamento):
    # n_nc=2,t_nc=30,n_ret=1,t_ret=15 => 75 minutos total => 08:00 -> 09:15
    assert str(agendamento.horario_final) == "09:15:00"
