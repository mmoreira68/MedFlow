import os
import django
import random
from datetime import datetime, timedelta, time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_config.settings')
django.setup()

from medflow.models import (
    Andar, Funcionalidade, Sala, Profissional,
    ProfissionalParametros, ProfissionalDiasAtendimento,
    ProfissionalEquipamento, Equipamento, AgendamentoSala
)

# Reset database (opcional e cuidadoso)
AgendamentoSala.objects.all().delete()
ProfissionalEquipamento.objects.all().delete()
ProfissionalDiasAtendimento.objects.all().delete()
ProfissionalParametros.objects.all().delete()
Sala.objects.all().delete()
Profissional.objects.all().delete()
Funcionalidade.objects.all().delete()
Andar.objects.all().delete()
Equipamento.objects.all().delete()

# Dados base
especialidades = ["Cardiologia", "Oftalmologia", "Ortopedia", "Pediatria", "Dermatologia"]
equipamentos_nomes = ["Estetoscópio", "Oftalmoscópio", "Bisturi", "Monitor cardíaco", "Ultrassom"]
dias_semana = ['SEG', 'TER', 'QUA', 'QUI', 'SEX']

# Criar equipamentos
equipamentos = [Equipamento.objects.create(nome=nome) for nome in equipamentos_nomes]

# Criar funcionalidades
funcionalidades = [Funcionalidade.objects.create(nome=nome) for nome in especialidades]

# Criar andares e salas
salas = []
for n in range(1, 4):
    andar = Andar.objects.create(numero=n)
    for i in range(1, 4):
        func = random.choice(funcionalidades)
        sala = Sala.objects.create(
            numero=n * 10 + i,
            nome=f"Sala {n}{i}",
            andar=andar,
            funcao=func
        )
        salas.append(sala)

# Criar profissionais com parâmetros, dias e equipamentos
profissionais = []
for i in range(5):
    nome = f"Dr. Exemplo {i+1}"
    esp = especialidades[i % len(especialidades)]
    prof = Profissional.objects.create(nome=nome, especialidade=esp)
    profissionais.append(prof)

    ProfissionalParametros.objects.create(
        profissional=prof,
        n_nc=2,
        t_nc=15,
        n_ret=1,
        t_ret=10
    )

    for dia in random.sample(dias_semana, 3):
        ProfissionalDiasAtendimento.objects.create(profissional=prof, dia_semana=dia)

    for eq in random.sample(equipamentos, 2):
        ProfissionalEquipamento.objects.create(profissional=prof, equipamento=eq)

# Gerar agendamentos noturnos para os próximos 30 dias
inicio = datetime(2025, 5, 15)
for dia in range(30):
    data_ag = inicio + timedelta(days=dia)
    hora_base = time(10, 0)
    for sala in salas:
        for prof in profissionais:
            # Pega os parâmetros do profissional
            try:
                parametros = prof.profissionalparametros
            except ProfissionalParametros.DoesNotExist:
                continue

            duracao = parametros.n_nc * parametros.t_nc + parametros.n_ret * parametros.t_ret
            h_inicio = hora_base
            h_fim = (datetime.combine(data_ag, h_inicio) + timedelta(minutes=duracao)).time()

            conflito = AgendamentoSala.objects.filter(
                sala=sala,
                data_agendamento=data_ag.date(),
                horario_inicio__lt=h_fim,
                horario_final__gt=h_inicio
            ).exists()

            if not conflito:
                AgendamentoSala.objects.create(
                    profissional=prof,
                    sala=sala,
                    data_agendamento=data_ag.date(),
                    horario_inicio=h_inicio
                )
                break  # só um agendamento por sala por dia

print("Banco populado com sucesso com dados sem conflito.")
