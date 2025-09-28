import pytest
from django.core.exceptions import ValidationError

from medflow.forms import AndarForm, FuncionalidadeForm, ProfissionalForm
from medflow.models import Andar, Funcionalidade, Profissional

@pytest.mark.django_db
def test_andar_form_duplica_mensagem():
    Andar.objects.create(nome="Térreo")
    form = AndarForm(data={"nome": "Terreo"})
    assert not form.is_valid()
    assert "Já existe um andar com esse nome." in form.errors["nome"]

@pytest.mark.django_db
def test_funcionalidade_form_duplica_mensagem():
    Funcionalidade.objects.create(nome="Consulta")
    form = FuncionalidadeForm(data={"nome": "consulta"})
    assert not form.is_valid()
    assert "Já existe uma funcionalidade com esse nome." in form.errors["nome"]

@pytest.mark.django_db
def test_profissional_form_crm_obrigatorio_unique():
    Profissional.objects.create(nome="A", especialidade="B", crm="X")
    # CRM faltando
    form = ProfissionalForm(data={"nome": "B", "especialidade": "C", "crm": ""})
    assert not form.is_valid()
    # CRM duplicado
    form2 = ProfissionalForm(data={"nome": "C", "especialidade": "D", "crm": "X"})
    assert not form2.is_valid()
