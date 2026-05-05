from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import unicodedata
import requests

from .models import (
    AgendamentoSala, Andar, Equipamento, Especialidade, Profissional,
    Sala, Funcionalidade
)


# ---------- util: normalização compatível com nome_norm ----------
def _normalize(s: str) -> str:
    """
    Remove acentos, baixa caixa, colapsa espaços.
    """
    if s is None:
        return ""
    s = s.strip()
    s = unicodedata.normalize('NFD', s)
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    s = ' '.join(s.split())  # colapsa espaços internos
    return s.lower()


# ------------------------------
# FORMULÁRIO DE AGENDAMENTO
# ------------------------------
class AgendamentoSalaForm(forms.ModelForm):
    class Meta:
        model = AgendamentoSala
        fields = ['profissional', 'sala', 'data_agendamento', 'horario_inicio']
        widgets = {
            'profissional': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'sala': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'data_agendamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'horario_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def verificar_feriado(self, data):
        """
        Consulta a BrasilAPI para verificar se a data é feriado nacional
        """
        ano = data.year
        url = f"https://brasilapi.com.br/api/feriados/v1/{ano}"

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            feriados = response.json()

            data_formatada = data.strftime("%Y-%m-%d")

            for feriado in feriados:
                if feriado.get("date") == data_formatada:
                    return feriado.get("name", "Feriado")

            return None

        except requests.RequestException:
            # Caso a API falhe, você pode:
            # 1. permitir continuar
            # 2. bloquear
            # 3. registrar log
            return None

    def clean(self):
        cleaned_data = super().clean()
        profissional = cleaned_data.get('profissional')
        sala = cleaned_data.get('sala')
        data_agendamento = cleaned_data.get('data_agendamento')
        horario_inicio = cleaned_data.get('horario_inicio')

        if not all([profissional, sala, data_agendamento, horario_inicio]):
            return cleaned_data

        # ----------------------------------
        # VALIDAÇÃO DE FERIADO
        # ----------------------------------
        nome_feriado = self.verificar_feriado(data_agendamento)

        if nome_feriado:
            raise ValidationError(
                f"Não é possível agendar nesta data pois é feriado: {nome_feriado}"
            )

        # ----------------------------------
        # VALIDAÇÃO DOS PARÂMETROS
        # ----------------------------------
        try:
            parametros = profissional.profissionalparametros
        except Profissional.profissionalparametros.RelatedObjectDoesNotExist:
            raise ValidationError("O profissional selecionado não possui parâmetros configurados.")

        duracao = parametros.n_nc * parametros.t_nc + parametros.n_ret * parametros.t_ret
        horario_final = (datetime.combine(data_agendamento, horario_inicio) + timedelta(minutes=duracao)).time()

        conflitos = AgendamentoSala.objects.filter(
            sala=sala,
            data_agendamento=data_agendamento
        ).exclude(pk=self.instance.pk)

        for ag in conflitos:
            if horario_inicio < ag.horario_final and horario_final > ag.horario_inicio:
                raise ValidationError("Conflito de horário: já existe um agendamento para esta sala neste período.")

        return cleaned_data


# ------------------------------
# FORMULÁRIO DE ANDAR
# ------------------------------
class AndarForm(forms.ModelForm):
    class Meta:
        model = Andar
        fields = ['nome']
        widgets = {"nome": forms.TextInput(attrs={"class": "form-control", "required": True})}

    def clean_nome(self):
        nome = (self.cleaned_data.get('nome') or '').strip()
        norm = _normalize(nome)
        qs = Andar.objects.filter(nome_norm=norm)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Já existe um andar com esse nome.')
        return nome


# ------------------------------
# FORMULÁRIO DE SALA
# ------------------------------
class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['numero', 'nome', 'andar', 'funcao']
        labels = {
            'numero': 'Número',
            'funcao': 'Funcionalidade',
            'nome': 'Nome',
            'andar': 'Andar',
        }
        widgets = {
            "numero": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "nome": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "andar": forms.Select(attrs={"class": "form-control", "required": True}),
            "funcao": forms.Select(attrs={"class": "form-control", "required": True}),
        }

class EspecialidadeForm(forms.ModelForm):
    class Meta:
        model = Especialidade
        fields = ["nome"]
        widgets = {"nome": forms.TextInput(attrs={"class": "form-control", "required": True})}


# ------------------------------
# FORMULÁRIO DE PROFISSIONAL
# ------------------------------
class ProfissionalForm(forms.ModelForm):
    class Meta:
        model = Profissional
        fields = ['nome', 'especialidade', 'crm']
        labels = {
            'nome': 'Nome',
            'especialidade': 'Especialidade',
            'crm': 'CRM',
        }
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "especialidade": forms.Select(attrs={"class": "form-control", "required": True}),
            "crm": forms.TextInput(attrs={"class": "form-control", "required": True}),
        }

    def clean_crm(self):
        crm = (self.cleaned_data.get('crm') or '').strip()
        if not crm:
            raise ValidationError('Informe o CRM.')
        qs = Profissional.objects.filter(crm__iexact=crm)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Já existe um profissional com este CRM.')
        return crm


# ------------------------------
# FORMULÁRIO DE FUNCIONALIDADE
# ------------------------------
class FuncionalidadeForm(forms.ModelForm):
    class Meta:
        model = Funcionalidade
        fields = ['nome']
        widgets = {"nome": forms.TextInput(attrs={"class": "form-control", "required": True})}

    def clean_nome(self):
        nome = (self.cleaned_data.get('nome') or '').strip()
        norm = _normalize(nome)
        qs = Funcionalidade.objects.filter(nome_norm=norm)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Já existe uma funcionalidade com esse nome.')
        return nome


# ------------------------------
# FORMULÁRIO DE EQUIPAMENTO
# ------------------------------
class EquipamentoForm(forms.ModelForm):
    class Meta:
        model = Equipamento
        fields = ['nome']
        widgets = {"nome": forms.TextInput(attrs={"class": "form-control", "required": True})}

    def clean_nome(self):
        nome = (self.cleaned_data.get('nome') or '').strip()
        norm = _normalize(nome)
        qs = Equipamento.objects.filter(nome_norm=norm)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Já existe um equipamento com esse nome.')
        return nome


# ------------------------------
# FORMULÁRIO DE PARÂMETROS DO PROFISSIONAL
# ------------------------------
DIAS_SEMANA = [
    ('SEG', 'Segunda-feira'),
    ('TER', 'Terça-feira'),
    ('QUA', 'Quarta-feira'),
    ('QUI', 'Quinta-feira'),
    ('SEX', 'Sexta-feira'),
    ('SAB', 'Sábado'),
    ('DOM', 'Domingo'),
]

class ParametrosProfissionalForm(forms.Form):
    profissional = forms.ModelChoiceField(queryset=Profissional.objects.all(), label="Profissional", widget=forms.Select(attrs={"class": "form-control", "required": True}))

    n_nc = forms.IntegerField(label="Nº atendimentos - Novo Caso", widget=forms.NumberInput(attrs={"class": "form-control", "required": True, "min": 0}))
    t_nc = forms.IntegerField(label="Tempo (min) - Novo Caso", widget=forms.NumberInput(attrs={"class": "form-control", "required": True, "min": 0}))
    n_ret = forms.IntegerField(label="Nº atendimentos - Retorno", widget=forms.NumberInput(attrs={"class": "form-control", "required": True, "min": 0}))
    t_ret = forms.IntegerField(label="Tempo (min) - Retorno", widget=forms.NumberInput(attrs={"class": "form-control", "required": True, "min": 0}))

    dias_atendimento = forms.MultipleChoiceField(
        choices=DIAS_SEMANA,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        label="Dias da semana",
    )

    equipamentos = forms.ModelMultipleChoiceField(
        queryset=Equipamento.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        label="Equipamentos necessários"
    )
