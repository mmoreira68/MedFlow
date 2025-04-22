from django.db import models

class Andar(models.Model):
    numero = models.IntegerField(unique=True)
    
    def __str__(self):
        return f"{self.numero}"

class Funcionalidade(models.Model):
    nome = models.CharField(max_length=100, unique=True)
   
    def __str__(self):
        return self.nome

class Sala(models.Model):
    numero = models.IntegerField(unique=True)
    nome = models.CharField(max_length=100, unique=True)
    andar = models.ForeignKey(Andar, on_delete=models.CASCADE)
    funcao = models.ForeignKey(Funcionalidade, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nome} - {self.funcao}"

class Equipamento(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    
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

class Profissional(models.Model):
    nome = models.CharField(max_length=100)
    especialidade = models.CharField(max_length=100)

    class Meta:
        unique_together = ("nome", "especialidade")

    def __str__(self):
        return f"{self.nome} - {self.especialidade}"

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
    dia_semana = models.CharField(
        max_length=3,
        choices=DiasDaSemana.choices
    )

    class Meta:
        unique_together = ("profissional", "dia_semana")

    def __str__(self):
        return f"{self.profissional} - {self.dia_semana}"

# ================================================================================
# ================================================================================

from datetime import datetime, timedelta

class AgendamentoSala(models.Model):
    profissional = models.ForeignKey('Profissional', on_delete=models.CASCADE)
    sala = models.ForeignKey('Sala', on_delete=models.CASCADE)
    horario_inicio = models.TimeField()
    horario_final = models.TimeField(editable=False)

    def save(self, *args, **kwargs):
        parametros = getattr(self.profissional, 'profissionalparametros', None)
        if not parametros:
            raise ValueError(f"Profissional {self.profissional} sem parâmetros.")

        minutos_totais = parametros.n_nc * parametros.t_nc + parametros.n_ret * parametros.t_ret
        inicio = datetime.combine(datetime.today(), self.horario_inicio)
        self.horario_final = (inicio + timedelta(minutes=minutos_totais)).time()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.profissional} - {self.sala} - ({self.horario_inicio} às {self.horario_final})"
