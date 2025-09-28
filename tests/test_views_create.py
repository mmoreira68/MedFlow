import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_criar_andar_post(auth_client):
    url = reverse("criar_andar")
    resp = auth_client.post(url, data={"nome": "Primeiro"}, follow=True)
    assert resp.status_code == 200
    assert "Andar" in resp.content.decode()  # voltou ao dashboard com mensagens/listas

@pytest.mark.django_db
def test_criar_equipamento_post(auth_client):
    url = reverse("criar_equipamento")
    resp = auth_client.post(url, data={"nome": "Ultrassom"}, follow=True)
    assert resp.status_code == 200

@pytest.mark.django_db
def test_criar_funcionalidade_post(auth_client):
    url = reverse("criar_funcionalidade")
    resp = auth_client.post(url, data={"nome": "Consulta"}, follow=True)
    assert resp.status_code == 200

@pytest.mark.django_db
def test_criar_profissional_post(auth_client):
    url = reverse("criar_profissional")
    resp = auth_client.post(url, data={
        "nome": "Dra Beta",
        "especialidade": "Ortopedia",
        "crm": "CRM987",
    }, follow=True)
    assert resp.status_code == 200
