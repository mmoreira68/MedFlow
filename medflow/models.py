from datetime import datetime, timedelta
from django.db import models
from django.db.models.deletion import PROTECT

from .models_mixins import UniqueNormalizedNameMixin, NormalizedNameMixin


class Andar(UniqueNormalizedNameMixin):
    class Meta(UniqueNormalizedNameMixin.Meta):
        verbose_name = "Andar"
        verbose_name_plural = "Andares"

    def __str__(self):
        return f"{self.nome}"


class Funcionalidade(UniqueNormalizedNameMixin):
    class Meta(UniqueNormalizedNameMixin.Meta):
        verbose_name = "Funcionalidade"
        verbose_name_plural = "Funcionalidades"

    def __str__(self):
        return self.nome


class Sala(models.Model):
    numero = models.IntegerField(unique=True, verbose_name="Número")
    nome = models.CharField(max_length=100, unique=True)
    # PROTECT para impedir excluir Andar com salas
    andar = models.ForeignKey(Andar, on_delete=PROTECT)
    funcao = models.ForeignKey(
        Funcionalidade,
        on_delete=models.CASCADE,
        max_length=50,
        verbose_name="Funcionalidade"
    )

    def __str__(self):
        return f"{self.nome} - {self.funcao}"


class Equipamento(UniqueNormalizedNameMixin):
    class Meta(UniqueNormalizedNameMixin.Meta):
        verbose_name = "Equipamento"
        verbose_name_plural = "Equipamentos"

    def __str__(self):
        return self.nome


class SalaEquipamento(models.Model):
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("sala", "equipamento")

    def __str__(self):
        return f"{self.sala} - {self.equipamento}"


# ================================================================================

class Profissional(NormalizedNameMixin):
    """
    Homônimos permitidos; diferencia por CRM único.
    """
    especialidade = models.CharField(max_length=100)
    crm = models.CharField(max_length=30, unique=True)

    class Meta(NormalizedNameMixin.Meta):
        verbose_name = "Profissional"
        verbose_name_plural = "Profissionais"

    def __str__(self):
        return f"{self.nome} - {self.especialidade} (CRM {self.crm})"


class ProfissionalEquipamento(models.Model):
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("profissional", "equipamento")

    def __str__(self):
        return f"{self.profissional} - {self.equipamento}"


class ProfissionalParametros(models.Model):
    profissional = models.OneToOneField(Profissional, on_delete=models.CASCADE)
    n_nc = models.IntegerField()
    t_nc = models.IntegerField()
    n_ret = models.IntegerField()
    t_ret = models.IntegerField()

    def __str__(self):
        return f"{self.profissional} - {self.n_nc} - {self.t_nc} - {self.n_ret} - {self.t_ret}"


class ProfissionalDiasAtendimento(models.Model):

    class DiasDaSemana(models.TextChoices):
        SEG, TER, QUA, QUI, SEX, SAB, DOM = ('SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SAB', 'DOM')

    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE)
    dia_semana = models.CharField(max_length=3, choices=DiasDaSemana.choices)

    class Meta:
        unique_together = ("profissional", "dia_semana")

    def __str__(self):
        return f"{self.profissional} - {self.dia_semana}"


# ================================================================================

class AgendamentoSala(models.Model):
    # PROTECT para impedir excluir Profissional com agendamento
    profissional = models.ForeignKey('Profissional', on_delete=PROTECT)
    # PROTECT para impedir excluir Sala com agendamento
    sala = models.ForeignKey('Sala', on_delete=PROTECT)
    data_agendamento = models.DateField(default='2025-01-01')
    horario_inicio = models.TimeField()
    horario_final = models.TimeField(editable=False)

    def save(self, *args, **kwargs):
        parametros = getattr(self.profissional, 'profissionalparametros', None)
        if not parametros:
            raise ValueError(f"Profissional {self.profissional} sem parâmetros.")

        inicio = datetime.combine(self.data_agendamento, self.horario_inicio)
        self.horario_final = (inicio + timedelta(
            minutes=(parametros.n_nc * parametros.t_nc + parametros.n_ret * parametros.t_ret)
        )).time()

        conflitos = AgendamentoSala.objects.filter(
            sala=self.sala,
            data_agendamento=self.data_agendamento
        ).exclude(pk=self.pk)

        for ag in conflitos:
            if (self.horario_inicio < ag.horario_final and self.horario_final > ag.horario_inicio):
                raise ValueError("Conflito de horário detectado com outro agendamento.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.profissional} - {self.sala} - ({self.horario_inicio} às {self.horario_final})"
