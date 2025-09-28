import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, time

from medflow.models import (
    Andar, Funcionalidade, Equipamento, Sala, Profissional,
    ProfissionalParametros, ProfissionalDiasAtendimento, AgendamentoSala
)

@pytest.fixture
def user(db):
    return User.objects.create_user(username="admin", password="admin")

@pytest.fixture
def auth_client(client, user):
    client.login(username="admin", password="admin")
    return client

# ---------- fábricas simples (sem libs externas) ----------

@pytest.fixture
def andar(db):
    return Andar.objects.create(nome="Térreo")

@pytest.fixture
def func(db):
    return Funcionalidade.objects.create(nome="Consulta")

@pytest.fixture
def equipamento(db):
    return Equipamento.objects.create(nome="Ultrassom")

@pytest.fixture
def sala(db, andar, func):
    # número único + nome único conforme seu model
    return Sala.objects.create(numero=101, nome="Sala A", andar=andar, funcao=func)

@pytest.fixture
def profissional(db):
    # CRM é único
    return Profissional.objects.create(nome="Dra. Ana", especialidade="Clínica Geral", crm="CRM123")

@pytest.fixture
def parametros(db, profissional):
    return ProfissionalParametros.objects.create(
        profissional=profissional, n_nc=2, t_nc=30, n_ret=1, t_ret=15
    )

@pytest.fixture
def agendamento(db, sala, profissional, parametros):
    # cria um agendamento simples
    return AgendamentoSala.objects.create(
        profissional=profissional,
        sala=sala,
        data_agendamento=date(2025, 1, 1),
        horario_inicio=time(8, 0),
    )

# ajuda para montar URLs com ?next=...
@pytest.fixture
def next_create_sala_url(db, andar):
    return reverse("criar_sala", args=[andar.pk])
