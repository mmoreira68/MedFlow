import os
import django
import random
from datetime import date, datetime, timedelta, time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_config.settings")
django.setup()

from medflow.models import (
    Andar, Funcionalidade, Sala, SalaEquipamento,
    Especialidade, Profissional,
    ProfissionalParametros, ProfissionalDiasAtendimento,
    ProfissionalEquipamento, Equipamento, AgendamentoSala,
)

random.seed(42)

# ── 1. Limpeza (ordem respeita FKs com PROTECT) ───────────────────────────────
print("Limpando banco...")
AgendamentoSala.objects.all().delete()
ProfissionalEquipamento.objects.all().delete()
ProfissionalDiasAtendimento.objects.all().delete()
ProfissionalParametros.objects.all().delete()
SalaEquipamento.objects.all().delete()
Sala.objects.all().delete()
Profissional.objects.all().delete()
Especialidade.objects.all().delete()
Funcionalidade.objects.all().delete()
Andar.objects.all().delete()
Equipamento.objects.all().delete()
print("Banco limpo.\n")

# ── 2. Andares ─────────────────────────────────────────────────────────────────
andares = {n: Andar.objects.create(nome=n)
           for n in ["Térreo", "1º Andar", "2º Andar"]}
print(f"[OK] {len(andares)} andares")

# ── 3. Funcionalidades ─────────────────────────────────────────────────────────
funcionalidades = {n: Funcionalidade.objects.create(nome=n)
                   for n in [
    "Consultório Clínico",
    "Sala de Cirurgia",
    "Sala de Radiologia",
    "Sala de Higienização",
    "Sala de Triagem",
]}
print(f"[OK]  {len(funcionalidades)} funcionalidades")

# ── 4. Equipamentos ────────────────────────────────────────────────────────────
equipamentos = {n: Equipamento.objects.create(nome=n)
                for n in [
    "Cadeira Odontológica",
    "Fotopolimerizador LED",
    "Motor de Alta Rotação",
    "Aparelho de Raio-X",
    "Autoclave",
    "Sugador Cirúrgico",
    "Compressor de Ar",
    "Ultrassom Odontológico",
    "Amalgamador",
    "Aparelho de Anestesia",
    "Foco de Luz LED",
    "Scanner Intraoral",
]}
print(f"[OK]  {len(equipamentos)} equipamentos")

# ── 5. Especialidades ──────────────────────────────────────────────────────────
especialidades = {n: Especialidade.objects.create(nome=n)
                  for n in [
    "Clínica Geral",
    "Ortodontia",
    "Endodontia",
    "Periodontia",
    "Cirurgia Bucomaxilofacial",
    "Implantodontia",
    "Odontopediatria",
    "Prótese Dentária",
    "Estética Dental",
]}
print(f"[OK]  {len(especialidades)} especialidades")

# ── 6. Salas — 3 andares × 10 salas = 30 ──────────────────────────────────────
#  Térreo   (100s): 2 Triagem, 2 Higienização, 6 Consultório Clínico
#  1º Andar (200s): 4 Consultório Clínico, 3 Cirurgia, 3 Radiologia
#  2º Andar (300s): 5 Consultório Clínico, 3 Cirurgia, 2 Higienização
LAYOUT = [
    ("Térreo",   1, [("Sala de Triagem", 2),     ("Sala de Higienização", 2), ("Consultório Clínico", 6)]),
    ("1º Andar", 2, [("Consultório Clínico", 4), ("Sala de Cirurgia", 3),    ("Sala de Radiologia", 3)]),
    ("2º Andar", 3, [("Consultório Clínico", 5), ("Sala de Cirurgia", 3),    ("Sala de Higienização", 2)]),
]

salas = []
for andar_nome, prefixo, grupos in LAYOUT:
    andar = andares[andar_nome]
    i = 0
    for func_nome, qtd in grupos:
        func = funcionalidades[func_nome]
        for _ in range(qtd):
            i += 1
            numero = prefixo * 100 + i
            sala = Sala.objects.create(
                numero=numero,
                nome=f"Sala {numero}",
                andar=andar,
                funcao=func,
            )
            salas.append(sala)

print(f"[OK]  {len(salas)} salas")

# Equipamentos por funcionalidade de sala
EQUIP_SALA = {
    "Consultório Clínico":  ["Cadeira Odontológica", "Motor de Alta Rotação",
                             "Fotopolimerizador LED", "Foco de Luz LED", "Compressor de Ar"],
    "Sala de Cirurgia":     ["Cadeira Odontológica", "Sugador Cirúrgico",
                             "Autoclave", "Aparelho de Anestesia", "Foco de Luz LED"],
    "Sala de Radiologia":   ["Aparelho de Raio-X", "Scanner Intraoral"],
    "Sala de Higienização": ["Cadeira Odontológica", "Ultrassom Odontológico", "Foco de Luz LED"],
    "Sala de Triagem":      ["Cadeira Odontológica", "Foco de Luz LED"],
}

for sala in salas:
    for eq_nome in EQUIP_SALA.get(sala.funcao.nome, []):
        SalaEquipamento.objects.create(sala=sala, equipamento=equipamentos[eq_nome])

print("[OK]  equipamentos nas salas")

# ── 7. Profissionais (25) ──────────────────────────────────────────────────────
# (nome, especialidade, crm, n_nc, t_nc, n_ret, t_ret, dias_trabalho)
PROFS = [
    # Clínica Geral (5)
    ("Dra. Ana Paula Ferreira",      "Clínica Geral",             "CRO-SP 12301",  2, 30, 1, 15, ["SEG","TER","QUA","QUI","SEX"]),
    ("Dr. Bruno Henrique Lima",      "Clínica Geral",             "CRO-SP 12302",  3, 20, 1, 10, ["SEG","QUA","SEX"]),
    ("Dra. Camila Dias Rocha",       "Clínica Geral",             "CRO-MG 22303",  2, 25, 1, 15, ["TER","QUI","SAB"]),
    ("Dr. Diego Martins Cunha",      "Clínica Geral",             "CRO-RJ 32304",  3, 20, 2, 10, ["SEG","TER","QUA"]),
    ("Dra. Elaine Souza Barros",     "Clínica Geral",             "CRO-SP 12305",  2, 30, 1, 15, ["QUA","QUI","SEX"]),
    # Ortodontia (3)
    ("Dr. Felipe Augusto Torres",    "Ortodontia",                "CRO-SP 12306",  1, 60, 1, 30, ["SEG","QUA","SEX"]),
    ("Dra. Gabriela Nunes Pinto",    "Ortodontia",                "CRO-MG 22307",  1, 50, 1, 25, ["TER","QUI"]),
    ("Dr. Henrique Castro Alves",    "Ortodontia",                "CRO-SP 12308",  1, 60, 1, 30, ["SEG","TER","SAB"]),
    # Endodontia (3)
    ("Dra. Isabela Ramos Vieira",    "Endodontia",                "CRO-SP 12309",  1, 90, 1, 30, ["TER","QUI","SEX"]),
    ("Dr. João Paulo Mendes",        "Endodontia",                "CRO-RJ 32310",  1, 80, 1, 30, ["SEG","QUA","SEX"]),
    ("Dra. Karla Oliveira Freitas",  "Endodontia",                "CRO-SP 12311",  1, 90, 1, 30, ["TER","QUI"]),
    # Periodontia (2)
    ("Dr. Lucas Figueiredo Santos",  "Periodontia",               "CRO-SP 12312",  1, 45, 1, 20, ["SEG","QUA","SEX"]),
    ("Dra. Mariana Costa Teixeira",  "Periodontia",               "CRO-MG 22313",  1, 45, 1, 20, ["TER","QUI","SAB"]),
    # Cirurgia Bucomaxilofacial (2)
    ("Dr. Nicolas Pereira Batista",  "Cirurgia Bucomaxilofacial", "CRO-SP 12314",  1, 120, 1, 45, ["SEG","QUA"]),
    ("Dra. Olivia Barbosa Cruz",     "Cirurgia Bucomaxilofacial", "CRO-RJ 32315",  1, 120, 1, 45, ["TER","QUI"]),
    # Implantodontia (2)
    ("Dr. Paulo Ricardo Andrade",    "Implantodontia",            "CRO-SP 12316",  1, 90, 1, 45, ["SEG","QUA","SEX"]),
    ("Dra. Quézia Lopes Moraes",     "Implantodontia",            "CRO-MG 22317",  1, 90, 1, 45, ["TER","QUI","SAB"]),
    # Odontopediatria (3)
    ("Dr. Rafael Albuquerque Lima",  "Odontopediatria",           "CRO-SP 12318",  2, 30, 1, 15, ["SEG","TER","QUA","QUI","SEX"]),
    ("Dra. Sabrina Cavalcanti Melo", "Odontopediatria",           "CRO-PE 42319",  2, 25, 1, 15, ["SEG","QUA","SEX"]),
    ("Dr. Thiago Rodrigues Vieira",  "Odontopediatria",           "CRO-SP 12320",  2, 30, 1, 15, ["TER","QUI","SAB"]),
    # Prótese Dentária (3)
    ("Dra. Úrsula Ferraz Gomes",     "Prótese Dentária",          "CRO-SP 12321",  1, 60, 1, 30, ["SEG","QUA","SEX"]),
    ("Dr. Vinicius Cardoso Leal",    "Prótese Dentária",          "CRO-MG 22322",  1, 60, 1, 30, ["TER","QUI"]),
    ("Dra. Wanda Peixoto Amaral",    "Prótese Dentária",          "CRO-RJ 32323",  1, 60, 1, 30, ["SEG","TER","SAB"]),
    # Estética Dental (2)
    ("Dr. Xavier Monteiro Farias",   "Estética Dental",           "CRO-SP 12324",  1, 60, 1, 20, ["SEG","QUA","SEX"]),
    ("Dra. Yasmin Duarte Silveira",  "Estética Dental",           "CRO-MG 22325",  1, 60, 1, 20, ["TER","QUI","SAB"]),
]

profissionais  = []
prof_duracao   = {}  # prof.id → duração em minutos
prof_dias_set  = {}  # prof.id → set de dias

for nome, esp_nome, crm, n_nc, t_nc, n_ret, t_ret, dias in PROFS:
    prof = Profissional.objects.create(
        nome=nome,
        especialidade=especialidades[esp_nome],
        crm=crm,
    )
    ProfissionalParametros.objects.create(
        profissional=prof,
        n_nc=n_nc, t_nc=t_nc, n_ret=n_ret, t_ret=t_ret,
    )
    for dia in dias:
        ProfissionalDiasAtendimento.objects.create(profissional=prof, dia_semana=dia)

    profissionais.append(prof)
    prof_duracao[prof.id]  = n_nc * t_nc + n_ret * t_ret
    prof_dias_set[prof.id] = set(dias)

print(f"[OK]  {len(profissionais)} profissionais")

# Equipamentos por especialidade do profissional
EQUIP_PROF = {
    "Clínica Geral":             ["Cadeira Odontológica", "Motor de Alta Rotação", "Fotopolimerizador LED"],
    "Ortodontia":                ["Cadeira Odontológica", "Scanner Intraoral"],
    "Endodontia":                ["Cadeira Odontológica", "Motor de Alta Rotação", "Aparelho de Raio-X"],
    "Periodontia":               ["Cadeira Odontológica", "Ultrassom Odontológico"],
    "Cirurgia Bucomaxilofacial": ["Cadeira Odontológica", "Sugador Cirúrgico", "Aparelho de Anestesia"],
    "Implantodontia":            ["Cadeira Odontológica", "Sugador Cirúrgico", "Scanner Intraoral"],
    "Odontopediatria":           ["Cadeira Odontológica", "Fotopolimerizador LED", "Foco de Luz LED"],
    "Prótese Dentária":          ["Cadeira Odontológica", "Scanner Intraoral", "Amalgamador"],
    "Estética Dental":           ["Cadeira Odontológica", "Fotopolimerizador LED", "Scanner Intraoral"],
}

for prof, (_, esp_nome, *_rest) in zip(profissionais, PROFS):
    for eq_nome in EQUIP_PROF.get(esp_nome, []):
        ProfissionalEquipamento.objects.create(
            profissional=prof, equipamento=equipamentos[eq_nome]
        )

print("[OK]  equipamentos nos profissionais")

# ── 8. Agendamentos — mês atual, máximo 150 ───────────────────────────────────
DIA_MAP    = {0: "SEG", 1: "TER", 2: "QUA", 3: "QUI", 4: "SEX", 5: "SAB", 6: "DOM"}
INICIO_DIA = time(8, 0)
FIM_DIA    = time(18, 0)
LIMITE     = 150

# Exclui Triagem e Radiologia (não são salas de consulta/atendimento)
salas_agenda = [s for s in salas
                if s.funcao.nome not in ("Sala de Triagem", "Sala de Radiologia")]

hoje        = date.today()
inicio_mes  = hoje.replace(day=1)
fim_mes     = (inicio_mes.replace(month=inicio_mes.month % 12 + 1, day=1)
               if inicio_mes.month < 12
               else inicio_mes.replace(year=inicio_mes.year + 1, month=1, day=1)
               ) - timedelta(days=1)

total = 0
data  = inicio_mes

print("\nGerando agendamentos", end="", flush=True)

while data <= fim_mes and total < LIMITE:
    dia_str     = DIA_MAP[data.weekday()]
    profs_hoje  = [p for p in profissionais if dia_str in prof_dias_set[p.id]]

    if not profs_hoje:
        data += timedelta(days=1)
        continue

    prof_livre: dict[int, time] = {p.id: INICIO_DIA for p in profs_hoje}

    random.shuffle(salas_agenda)

    for sala in salas_agenda:
        if total >= LIMITE:
            break
        h_sala     = INICIO_DIA
        candidatos = list(profs_hoje)
        random.shuffle(candidatos)

        while h_sala < FIM_DIA and total < LIMITE:
            agendado = False

            for prof in candidatos:
                dur      = timedelta(minutes=prof_duracao[prof.id])
                h_inicio = max(h_sala, prof_livre[prof.id])
                h_fim    = (datetime.combine(data, h_inicio) + dur).time()

                if h_fim > FIM_DIA:
                    continue

                try:
                    AgendamentoSala.objects.create(
                        profissional=prof,
                        sala=sala,
                        data_agendamento=data,
                        horario_inicio=h_inicio,
                    )
                    h_sala              = h_fim
                    prof_livre[prof.id] = h_fim
                    total              += 1
                    agendado            = True
                    break
                except ValueError:
                    continue

            if not agendado:
                proximos = [prof_livre[p.id] for p in candidatos
                            if prof_livre[p.id] > h_sala]
                if proximos:
                    h_sala = min(proximos)
                else:
                    break

    data += timedelta(days=1)
    print(".", end="", flush=True)

print(f"\n[OK]  {total} agendamentos\n")
print("Banco populado com sucesso!")
