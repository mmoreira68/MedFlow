import pytest
from django.core.exceptions import ValidationError

from medflow.forms import AndarForm, FuncionalidadeForm, ProfissionalForm
from medflow.models import Andar, Funcionalidade, Profissional, Especialidade

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
    esp = Especialidade.objects.create(nome="Clínica Geral")
    Profissional.objects.create(nome="A", especialidade=esp, crm="X")
    # CRM faltando
    esp2 = Especialidade.objects.create(nome="Cardiologia")

    form = ProfissionalForm(data={
        "nome": "B",
        "especialidade": esp2.id,
        "crm": ""
    })
    assert not form.is_valid()
    # CRM duplicado
    form2 = ProfissionalForm(data={
        "nome": "C",
        "especialidade": esp2.id,
        "crm": "X"
    })
    assert not form2.is_valid()
