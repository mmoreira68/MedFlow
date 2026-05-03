import pytest
from datetime import date, time, timedelta

from django.core.cache import cache
from rest_framework.test import APIRequestFactory

from medflow.api.views import PublicAgendamentoViewSet
from medflow.models import AgendamentoSala, Andar, Especialidade, Funcionalidade, Profissional, ProfissionalParametros, Sala


@pytest.fixture
def factory():
    return APIRequestFactory()


@pytest.fixture
def andar(db):
    return Andar.objects.create(
        nome="Térreo",
    )

@pytest.fixture
def funcionalidade(db):
    return Funcionalidade.objects.create(
        nome="Consultório",
    )



@pytest.fixture
def sala(db, andar, funcionalidade):
    return Sala.objects.create(
        nome="Sala Teste",
        numero="101",
        andar=andar,
        funcao=funcionalidade
    )

@pytest.fixture
def especialidade(db):
    return Especialidade.objects.create(
        nome="Cardiologia"
    )


@pytest.fixture
def profissional(db, especialidade):
    return Profissional.objects.create(
        nome="Dr. João",
        especialidade=especialidade,
        crm="12345"
    )

@pytest.fixture
def profissional_parametros(db, profissional):
    return ProfissionalParametros.objects.create(
        profissional=profissional,
        n_nc=10,
        t_nc=30,
        n_ret=5,
        t_ret=15,
    )


@pytest.fixture
def agendamento_futuro(
    db,
    sala,
    profissional,
    profissional_parametros,
):
    return AgendamentoSala.objects.create(
        sala=sala,
        profissional=profissional,
        data_agendamento=date.today() + timedelta(days=1),
        horario_inicio=time(9, 0),
        horario_final=time(10, 0),
    )


@pytest.fixture
def agendamento_passado(
    db,
    sala,
    profissional,
    profissional_parametros,
):
    return AgendamentoSala.objects.create(
        sala=sala,
        profissional=profissional,
        data_agendamento=date.today() - timedelta(days=1),
        horario_inicio=time(8, 0),
        horario_final=time(9, 0),
    )


@pytest.mark.django_db
def test_get_queryset_retorna_apenas_futuros(
    agendamento_futuro,
    agendamento_passado,
):
    viewset = PublicAgendamentoViewSet()

    queryset = viewset.get_queryset()

    assert agendamento_futuro in queryset
    assert agendamento_passado not in queryset


@pytest.mark.django_db
def test_calendar_disponibilidade_retorna_dados(
    factory,
    agendamento_futuro,
    especialidade
):
    view = PublicAgendamentoViewSet.as_view(
        {"get": "calendar_disponibilidade"}
    )

    request = factory.get(
        "/api/public/agendamentos/calendar/disponibilidade/",
        {
            "data_inicio": str(date.today()),
            "data_fim": str(date.today() + timedelta(days=5)),
        },
    )

    response = view(request)

    assert response.status_code == 200
    assert "datas" in response.data
    assert "periodo" in response.data
    assert len(response.data["datas"]) == 1

    horario = response.data["datas"][0]["horarios"][0]

    assert horario["inicio"] == "09:00"
    assert horario["fim"] == agendamento_futuro.horario_final.strftime("%H:%M")
    assert horario["sala"] == "Sala Teste"
    assert horario["profissional"] == "Dr. João"
    assert horario["especialidade"] == especialidade.nome


@pytest.mark.django_db
def test_calendar_disponibilidade_data_invalida_retorna_400(factory):
    view = PublicAgendamentoViewSet.as_view(
        {"get": "calendar_disponibilidade"}
    )

    request = factory.get(
        "/api/public/agendamentos/calendar/disponibilidade/",
        {
            "data_inicio": "data-invalida",
            "data_fim": "2026-12-31",
        },
    )

    response = view(request)

    assert response.status_code == 400
    assert response.data["erro"] == "Datas inválidas. Use formato YYYY-MM-DD"


@pytest.mark.django_db
def test_dias_com_agendamentos_retorna_datas(
    factory,
    agendamento_futuro,
):
    view = PublicAgendamentoViewSet.as_view(
        {"get": "dias_com_agendamentos"}
    )

    request = factory.get(
        "/api/public/agendamentos/dias-com-agendamentos/",
        {
            "data_inicio": str(date.today()),
            "data_fim": str(date.today() + timedelta(days=5)),
        },
    )

    response = view(request)

    assert response.status_code == 200
    assert "datas" in response.data
    assert "total" in response.data
    assert response.data["total"] == 1
    assert str(agendamento_futuro.data_agendamento) in response.data["datas"]


@pytest.mark.django_db
def test_dias_com_agendamentos_data_invalida_retorna_400(factory):
    view = PublicAgendamentoViewSet.as_view(
        {"get": "dias_com_agendamentos"}
    )

    request = factory.get(
        "/api/public/agendamentos/dias-com-agendamentos/",
        {
            "data_inicio": "xxxx",
            "data_fim": "2026-12-31",
        },
    )

    response = view(request)

    assert response.status_code == 400
    assert response.data["erro"] == "Datas inválidas. Use formato YYYY-MM-DD"


@pytest.mark.django_db
def test_calendar_disponibilidade_usa_cache(
    factory,
    agendamento_futuro,
):
    cache.clear()

    view = PublicAgendamentoViewSet.as_view(
        {"get": "calendar_disponibilidade"}
    )

    params = {
        "data_inicio": str(date.today()),
        "data_fim": str(date.today() + timedelta(days=5)),
    }

    request = factory.get(
        "/api/public/agendamentos/calendar/disponibilidade/",
        params,
    )

    response = view(request)

    assert response.status_code == 200

    cache_key = f"agendamentos:calendario:{request.GET.urlencode()}"
    cached_data = cache.get(cache_key)

    assert cached_data is not None
    assert "datas" in cached_data