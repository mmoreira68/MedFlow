from django.contrib import admin
from .models import (
    Andar, Funcionalidade, Sala,
    Equipamento, SalaEquipamento,
    Profissional, ProfissionalEquipamento, ProfissionalParametros,
    ProfissionalDiasAtendimento,
    AgendamentoSala, Especialidade
)

@admin.register(Andar)
class AndarAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome", "nome_norm")

@admin.register(Funcionalidade)
class FuncionalidadeAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome", "nome_norm")

@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ("andar","nome","funcao",)
    search_fields = ("nome",)
    list_filter = ("andar", "funcao")

@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome", "nome_norm")

@admin.register(SalaEquipamento)
class SalaEquipamentoAdmin(admin.ModelAdmin):
    list_display = ("sala","equipamento",)

# NOVO
@admin.register(Especialidade)
class EspecialidadeAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome", "nome_norm")

@admin.register(Profissional)
class ProfissionalAdmin(admin.ModelAdmin):
    list_display = ("nome","especialidade","crm")
    search_fields = ("nome", "nome_norm", "especialidade__nome", "crm")
    list_filter = ("especialidade",)

@admin.register(ProfissionalEquipamento)
class ProfissionalEquipamentoAdmin(admin.ModelAdmin):
    list_display = ("profissional","equipamento",)

@admin.register(ProfissionalParametros)
class ProfissionalParametrosAdmin(admin.ModelAdmin):
    list_display = ("profissional","n_nc","t_nc","n_ret","t_ret",)

@admin.register(ProfissionalDiasAtendimento)
class ProfissionalDiasAtendimentoAdmin(admin.ModelAdmin):
    list_display = ("profissional","dia_semana",)

@admin.register(AgendamentoSala)
class AgendamentoSalaAdmin(admin.ModelAdmin):
    list_display = ("profissional","sala","horario_inicio","horario_final",)
    list_filter = ("data_agendamento", "sala", "profissional")
