from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, date, timedelta
from datetime import date
from .models import Andar, Funcionalidade, ProfissionalDiasAtendimento, ProfissionalEquipamento, ProfissionalParametros, Sala, AgendamentoSala, Profissional
from .forms import AgendamentoSalaForm, AndarForm, FuncionalidadeForm, ProfissionalForm, SalaForm

# Página inicial
def home(request):
    return render(request, 'home.html')

# Página pública com agendamentos do dia (com navegação entre datas)
def visualizar_agendamentos(request):
    data_str = request.GET.get('data')
    try:
        data = datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else date.today()
    except ValueError:
        data = date.today()

    agendamentos = AgendamentoSala.objects.filter(data_agendamento=data).order_by('sala__nome', 'horario_inicio')

    return render(request, 'agendamentos_publico.html', {
        'agendamentos': agendamentos,
        'data': data,
        'data_anterior': data - timedelta(days=1),
        'data_posterior': data + timedelta(days=1),
    })

# Tela de login
def login_view(request):
    if request.method == "POST":
        username = request.POST['email']
        password = request.POST['senha']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    return render(request, 'login.html')

# Logout
@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

# Painel principal com lista de andares e salas
@login_required
def dashboard(request):
    andares = Andar.objects.prefetch_related('sala_set').all()
    profissionais = Profissional.objects.all()
    funcionalidades = Funcionalidade.objects.all()

    return render(request, 'dashboard.html', {
        'andares': andares,
        'profissionais': profissionais,
        'funcionalidades': funcionalidades,
    })

# Agendar sala (acessado a partir do dashboard)
@login_required
def agendar_sala(request, sala_id):
    sala = get_object_or_404(Sala, id=sala_id)
    if request.method == 'POST':
        form = AgendamentoSalaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = AgendamentoSalaForm(initial={'sala': sala})

    return render(request, 'agendar_sala.html', {'form': form, 'sala': sala})

@login_required
def lista_agendamentos(request):
    data_str = request.GET.get('data')
    try:
        data = datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else date.today()
    except ValueError:
        data = date.today()

    agendamentos = AgendamentoSala.objects.filter(data_agendamento=data).order_by('sala__nome', 'horario_inicio')

    profissional_id = request.GET.get('profissional')
    sala_id = request.GET.get('sala')

    if profissional_id:
        agendamentos = agendamentos.filter(profissional_id=profissional_id)

    if sala_id:
        agendamentos = agendamentos.filter(sala_id=sala_id)

    context = {
        'data': data,
        'data_anterior': data - timedelta(days=1),
        'data_posterior': data + timedelta(days=1),
        'agendamentos': agendamentos,
        'profissionais': Profissional.objects.all(),
        'salas': Sala.objects.all(),
        'profissional_id': profissional_id,
        'sala_id': sala_id
    }
    return render(request, 'agendamentos.html', context)

@login_required
def criar_andar(request):
    if request.method == 'POST':
        form = AndarForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = AndarForm()
    return render(request, 'form_generic.html', {'form': form, 'titulo': 'Criar Andar'})

@login_required
def criar_sala(request, andar_id):
    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = SalaForm(initial={'andar': andar_id})
    return render(request, 'form_generic.html', {'form': form, 'titulo': 'Criar Sala'})

@login_required
def criar_profissional(request):
    if request.method == 'POST':
        form = ProfissionalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProfissionalForm()
    return render(request, 'form_generic.html', {'form': form, 'titulo': 'Criar Profissional'})

@login_required
def criar_funcionalidade(request):
    from .forms import FuncionalidadeForm

    if request.method == 'POST':
        form = FuncionalidadeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = FuncionalidadeForm()
    return render(request, 'form_generic.html', {'form': form, 'titulo': 'Criar Funcionalidade'})

@login_required
def configurar_profissional(request):
    from .forms import ParametrosProfissionalForm

    if request.method == 'POST':
        form = ParametrosProfissionalForm(request.POST)
        if form.is_valid():
            profissional = form.cleaned_data['profissional']

            # Cadastra ou atualiza parâmetros
            parametros, _ = ProfissionalParametros.objects.update_or_create(
                profissional=profissional,
                defaults={
                    'n_nc': form.cleaned_data['n_nc'],
                    't_nc': form.cleaned_data['t_nc'],
                    'n_ret': form.cleaned_data['n_ret'],
                    't_ret': form.cleaned_data['t_ret'],
                }
            )

            # Dias de atendimento
            ProfissionalDiasAtendimento.objects.filter(profissional=profissional).delete()
            for dia in form.cleaned_data['dias_atendimento']:
                ProfissionalDiasAtendimento.objects.create(profissional=profissional, dia_semana=dia)

            # Equipamentos
            ProfissionalEquipamento.objects.filter(profissional=profissional).delete()
            for equipamento in form.cleaned_data['equipamentos']:
                ProfissionalEquipamento.objects.create(profissional=profissional, equipamento=equipamento)

            messages.success(request, 'Configurações salvas com sucesso.')
            return redirect('dashboard')
    else:
        form = ParametrosProfissionalForm()

    return render(request, 'form_generic.html', {'form': form, 'titulo': 'Configurar Profissional'})

# =========================
# CRUD PARA FUNCIONALIDADE
# =========================
@login_required
def editar_funcionalidade(request, pk):
    funcionalidade = get_object_or_404(Funcionalidade, pk=pk)
    if request.method == 'POST':
        form = FuncionalidadeForm(request.POST, instance=funcionalidade)
        if form.is_valid():
            form.save()
            messages.success(request, "Funcionalidade atualizada com sucesso.")
            return redirect('dashboard')
    else:
        form = FuncionalidadeForm(instance=funcionalidade)
    return render(request, 'form_generic.html', {'form': form, 'titulo': 'Editar Funcionalidade'})

@login_required
def excluir_funcionalidade(request, pk):
    funcionalidade = get_object_or_404(Funcionalidade, pk=pk)
    if request.method == 'POST':
        funcionalidade.delete()
        messages.success(request, "Funcionalidade excluída com sucesso.")
        return redirect('dashboard')
    return render(request, 'confirm_delete.html', {
        'objeto': funcionalidade,
        'titulo': 'Excluir Funcionalidade',
        'descricao': 'Tem certeza que deseja excluir esta funcionalidade?'
    })

# =========================
# CRUD PARA PROFISSIONAL
# =========================
@login_required
def editar_profissional(request, pk):
    profissional = get_object_or_404(Profissional, pk=pk)
    if request.method == 'POST':
        form = ProfissionalForm(request.POST, instance=profissional)
        if form.is_valid():
            form.save()
            messages.success(request, "Profissional atualizado com sucesso.")
            return redirect('dashboard')
    else:
        form = ProfissionalForm(instance=profissional)
    return render(request, 'form_generic.html', {'form': form, 'titulo': 'Editar Profissional'})

@login_required
def excluir_profissional(request, pk):
    profissional = get_object_or_404(Profissional, pk=pk)
    if request.method == 'POST':
        profissional.delete()
        messages.success(request, "Profissional excluído com sucesso.")
        return redirect('dashboard')
    return render(request, 'confirm_delete.html', {
        'objeto': profissional,
        'titulo': 'Excluir Profissional',
        'descricao': 'Tem certeza que deseja excluir este profissional?'
    })

# =========================
# CRUD PARA ANDAR
# =========================
@login_required
def editar_andar(request, pk):
    andar = get_object_or_404(Andar, pk=pk)
    if request.method == 'POST':
        form = AndarForm(request.POST, instance=andar)
        if form.is_valid():
            form.save()
            messages.success(request, "Andar atualizado com sucesso.")
            return redirect('dashboard')
    else:
        form = AndarForm(instance=andar)
    return render(request, 'form_generic.html', {'form': form, 'titulo': 'Editar Andar'})

@login_required
def excluir_andar(request, pk):
    andar = get_object_or_404(Andar, pk=pk)
    if request.method == 'POST':
        andar.delete()
        messages.success(request, "Andar excluído com sucesso.")
        return redirect('dashboard')
    return render(request, 'confirm_delete.html', {
        'objeto': andar,
        'titulo': 'Excluir Andar',
        'descricao': 'Tem certeza que deseja excluir este andar?'
    })

# =========================
# CRUD PARA SALA
# =========================
@login_required
def editar_sala(request, pk):
    sala = get_object_or_404(Sala, pk=pk)
    if request.method == 'POST':
        form = SalaForm(request.POST, instance=sala)
        if form.is_valid():
            form.save()
            messages.success(request, "Sala atualizada com sucesso.")
            return redirect('dashboard')
    else:
        form = SalaForm(instance=sala)
    return render(request, 'form_generic.html', {'form': form, 'titulo': 'Editar Sala'})

@login_required
def excluir_sala(request, pk):
    sala = get_object_or_404(Sala, pk=pk)
    if request.method == 'POST':
        sala.delete()
        messages.success(request, "Sala excluída com sucesso.")
        return redirect('dashboard')
    return render(request, 'confirm_delete.html', {
        'objeto': sala,
        'titulo': 'Excluir Sala',
        'descricao': 'Tem certeza que deseja excluir esta sala?'
    })

@login_required
def novo_agendamento(request):
    if request.method == 'POST':
        form = AgendamentoSalaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Agendamento criado com sucesso!")
            return redirect('lista_agendamentos')
    else:
        form = AgendamentoSalaForm()
    return render(request, 'form_generic.html', {
        'form': form,
        'titulo': 'Novo Agendamento'
    })

