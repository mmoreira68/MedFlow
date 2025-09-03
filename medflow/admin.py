from django.contrib import admin

from .models import Andar, Funcionalidade, Sala, \
                    Equipamento, SalaEquipamento, \
                    Profissional, ProfissionalEquipamento, ProfissionalParametros, \
                    ProfissionalDiasAtendimento, \
                    AgendamentoSala
                    
class AndarAdmin(admin.ModelAdmin):
    list_display = ("nome",)
admin.site.register(Andar, AndarAdmin)

class FuncionalidadeAdmin(admin.ModelAdmin):
    list_display = ("nome",)
admin.site.register(Funcionalidade, FuncionalidadeAdmin)

class SalaAdmin(admin.ModelAdmin):
    list_display = ("andar","nome","funcao",)
admin.site.register(Sala, SalaAdmin)

class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ("nome",)
admin.site.register(Equipamento, EquipamentoAdmin)

class SalaEquipamentoAdmin(admin.ModelAdmin):
    list_display = ("sala","equipamento",)
admin.site.register(SalaEquipamento, SalaEquipamentoAdmin)

# ================================================================================

class ProfissionalAdmin(admin.ModelAdmin):
    list_display = ("nome","especialidade",)
admin.site.register(Profissional, ProfissionalAdmin)

class ProfissionalEquipamentoAdmin(admin.ModelAdmin):
    list_display = ("profissional","equipamento",)
admin.site.register(ProfissionalEquipamento, ProfissionalEquipamentoAdmin)

class ProfissionalParametrosAdmin(admin.ModelAdmin):
    list_display = ("profissional","n_nc","t_nc","n_ret","t_ret",)
admin.site.register(ProfissionalParametros, ProfissionalParametrosAdmin)

class ProfissionalDiasAtendimentoAdmin(admin.ModelAdmin):
    list_display = ("profissional","dia_semana",)
admin.site.register(ProfissionalDiasAtendimento, ProfissionalDiasAtendimentoAdmin)

# ================================================================================
# ================================================================================

class AgendamentoSalaAdmin(admin.ModelAdmin):
    list_display = ("profissional","sala","horario_inicio","horario_final",)
admin.site.register(AgendamentoSala, AgendamentoSalaAdmin)

# class AgendamentoSala(models.Model):
#     profissional = models.ForeignKey('Profissional', on_delete=models.CASCADE)
#     sala_equipamento = models.ForeignKey('SalaEquipamento', on_delete=models.CASCADE)
#     horario_inicio = models.TimeField()
#     horario_final = models.TimeField(editable=False)
