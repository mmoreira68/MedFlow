from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

from .models import (
    AgendamentoSala, Andar, Equipamento, Profissional,
    Sala, Funcionalidade
)
from .utils.text import normalize_sans_accents

# ------------------------------
# FORMULÁRIO DE AGENDAMENTO
# ------------------------------
class AgendamentoSalaForm(forms.ModelForm):
    class Meta:
        model = AgendamentoSala
        fields = ['profissional', 'sala', 'data_agendamento', 'horario_inicio']
        widgets = {
            'data_agendamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'horario_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        profissional = cleaned_data.get('profissional')
        sala = cleaned_data.get('sala')
        data_agendamento = cleaned_data.get('data_agendamento')
        horario_inicio = cleaned_data.get('horario_inicio')

        if not all([profissional, sala, data_agendamento, horario_inicio]):
            return cleaned_data  # permite o Django exibir erros padrões

        try:
            parametros = profissional.profissionalparametros
        except Profissional.profissionalparametros.RelatedObjectDoesNotExist:
            raise ValidationError("O profissional selecionado não possui parâmetros configurados.")

        # Calcula o horário final baseado nos parâmetros do profissional
        duracao = parametros.n_nc * parametros.t_nc + parametros.n_ret * parametros.t_ret
        horario_final = (datetime.combine(data_agendamento, horario_inicio) + timedelta(minutes=duracao)).time()

        # Verifica conflitos na sala
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

    def clean_nome(self):
        nome = self.cleaned_data['nome'].strip()
        norm = normalize_sans_accents(nome)
        # nome_norm é único
        if Andar.objects.filter(nome_norm=norm).exists():
            raise ValidationError('Já existe um andar com esse nome (ignorando acentos/caixa).')
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

# ------------------------------
# FORMULÁRIO DE PROFISSIONAL
# ------------------------------
class ProfissionalForm(forms.ModelForm):
    class Meta:
        model = Profissional
        fields = ['nome', 'especialidade', 'crm']

    def clean_nome(self):
        # apenas consistência; não bloqueia homônimos
        nome = self.cleaned_data['nome'].strip()
        return nome

    def clean_crm(self):
        crm = self.cleaned_data['crm'].strip().upper()
        # você pode adicionar regex/validador de formato aqui, se quiser (ex: UF + dígitos)
        # Exemplo simples: somente alfanumérico, hífen e barra
        # import re
        # if not re.match(r'^[A-Z0-9\-\/\.]+$', crm):
        #     raise ValidationError('CRM em formato inválido.')
        # unicidade é garantida pelo unique=True do model; mas checamos cedo:
        qs = Profissional.objects.all()
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.filter(crm__iexact=crm).exists():
            raise ValidationError('Já existe um profissional com este CRM.')
        return crm

# ------------------------------
# FORMULÁRIO DE FUNCIONALIDADE
# ------------------------------
class FuncionalidadeForm(forms.ModelForm):
    class Meta:
        model = Funcionalidade
        fields = ['nome']
    
    def clean_nome(self):
        nome = self.cleaned_data['nome'].strip()
        norm = normalize_sans_accents(nome)
        if Funcionalidade.objects.filter(nome_norm=norm).exists():
            raise ValidationError('Já existe uma funcionalidade com esse nome (ignorando acentos/caixa).')
        return nome

# ------------------------------
# FORMULÁRIO DE EQUIPAMENTO
# ------------------------------
class EquipamentoForm(forms.ModelForm):
    class Meta:
        model = Equipamento
        fields = ['nome']

    def clean_nome(self):
        nome = self.cleaned_data['nome'].strip()
        norm = normalize_sans_accents(nome)
        if Equipamento.objects.filter(nome_norm=norm).exists():
            raise ValidationError('Já existe um equipamento com esse nome (ignorando acentos/caixa).')
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
    profissional = forms.ModelChoiceField(queryset=Profissional.objects.all(), label="Profissional")

    n_nc = forms.IntegerField(label="Nº atendimentos - Novo Caso")
    t_nc = forms.IntegerField(label="Tempo (min) - Novo Caso")
    n_ret = forms.IntegerField(label="Nº atendimentos - Retorno")
    t_ret = forms.IntegerField(label="Tempo (min) - Retorno")

    dias_atendimento = forms.MultipleChoiceField(
        choices=DIAS_SEMANA,
        widget=forms.CheckboxSelectMultiple,
        label="Dias da semana"
    )

    equipamentos = forms.ModelMultipleChoiceField(
        queryset=Equipamento.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Equipamentos necessários"
    )
