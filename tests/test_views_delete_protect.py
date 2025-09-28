import pytest
from django.urls import reverse
from django.db.models.deletion import ProtectedError

from medflow.models import Andar, Sala, AgendamentoSala

@pytest.mark.django_db
def test_excluir_sala_bloqueada_por_agendamento(auth_client, sala, agendamento):
    # tenta excluir sala com agendamento -> deve mostrar mensagem de erro e redirecionar
    url = f"{reverse('excluir_sala', args=[sala.pk])}?next={reverse('criar_sala', args=[sala.andar.pk])}"
    resp_get = auth_client.get(url)
    assert resp_get.status_code == 200  # página de confirmação

    resp_post = auth_client.post(url, data={"next": reverse('criar_sala', args=[sala.andar.pk])}, follow=True)
    html = resp_post.content.decode()
    # A view captura ProtectedError e mostra a mensagem:
    # "Não é possível excluir esta sala: existem agendamentos vinculados a ela."
    assert "Não é possível excluir esta sala" in html

@pytest.mark.django_db
def test_excluir_andar_bloqueado_por_sala(auth_client, sala):
    # Tenta excluir o andar que tem sala; com on_delete=PROTECT deve bloquear
    url = f"{reverse('excluir_andar', args=[sala.andar.pk])}?next={reverse('criar_andar')}"
    resp_get = auth_client.get(url)
    assert resp_get.status_code == 200

    resp_post = auth_client.post(url, data={"next": reverse('criar_andar')}, follow=True)
    html = resp_post.content.decode()
    # Mensagem configurada na view de excluir_andar
    assert "Não é possível excluir este andar" in html

@pytest.mark.django_db
def test_excluir_profissional_bloqueado_por_agendamento(auth_client, agendamento):
    prof = agendamento.profissional
    url = f"{reverse('excluir_profissional', args=[prof.pk])}?next={reverse('criar_profissional')}"
    resp_get = auth_client.get(url)
    assert resp_get.status_code == 200

    resp_post = auth_client.post(url, data={"next": reverse('criar_profissional')}, follow=True)
    html = resp_post.content.decode()
    assert "Não é possível excluir este profissional" in html
