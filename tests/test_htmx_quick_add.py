import pytest
from django.urls import reverse
from medflow.models import Andar, Funcionalidade

@pytest.mark.django_db
def test_andar_quick_add_get_returns_partial(auth_client):
    url = reverse("andar_quick_add")
    resp = auth_client.get(url)
    assert resp.status_code == 200
    assert "<form" in resp.content.decode().lower()

@pytest.mark.django_db
def test_andar_quick_add_post_ok(auth_client):
    url = reverse("andar_quick_add")
    resp = auth_client.post(url, data={"nome": "Térreo"})
    # Quando ok, devolve <option ...> e headers HTMX
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "<option" in html
    assert resp.headers.get("HX-Reswap") == "beforeend"

@pytest.mark.django_db
def test_andar_quick_add_post_duplicado(auth_client):
    Andar.objects.create(nome="Térreo")
    url = reverse("andar_quick_add")
    resp = auth_client.post(url, data={"nome": "Terreo"})
    # Re-renderiza o form com erro (status 200 também)
    assert resp.status_code == 200
    assert "Já existe um andar com esse nome." in resp.content.decode()

@pytest.mark.django_db
def test_func_quick_add_post_duplicado(auth_client):
    Funcionalidade.objects.create(nome="Consulta")
    url = reverse("func_quick_add")
    resp = auth_client.post(url, data={"nome": "consulta"})
    assert resp.status_code == 200
    assert "Já existe uma funcionalidade com esse nome." in resp.content.decode()
