import json
from sqlite3 import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from datetime import datetime, date, timedelta
from datetime import date

from .models import (
    Andar, Funcionalidade, Equipamento, ProfissionalDiasAtendimento,
    ProfissionalEquipamento, ProfissionalParametros, Sala, AgendamentoSala, Profissional
)
from .forms import (
    AgendamentoSalaForm, AndarForm, FuncionalidadeForm, ProfissionalForm,
    SalaForm, EquipamentoForm, ParametrosProfissionalForm
)

# ===== Helpers =====
def _current_path(request):
    return request.get_full_path()

def _safe_redirect(request, fallback_name='dashboard'):
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect(fallback_name)

def _ctx_lista(titulo, headers, rows, vazio_msg, subtitulo=None, mostra_acoes=True):
    return {
        'lista_titulo': titulo,
        'lista_subtitulo': subtitulo,
        'lista_headers': headers,
        'lista_rows': rows,
        'lista_vazia_msg': vazio_msg,
        'lista_mostra_acoes': mostra_acoes,
    }

def _row(cols, edit_url, delete_url):
    return {"cols": cols, "edit": edit_url, "delete": delete_url}


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

# Painel principal
@login_required
def dashboard(request):
    andares = Andar.objects.prefetch_related('sala_set').all()
    profissionais = Profissional.objects.all()
    funcionalidades = Funcionalidade.objects.all()
    equipamentos = Equipamento.objects.all()

    return render(request, 'dashboard.html', {
        'andares': andares,
        'profissionais': profissionais,
        'funcionalidades': funcionalidades,
        'equipamentos': equipamentos,
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

# =========================
# CRIAR (botão Cancelar -> dashboard) + listas abaixo
# =========================
@login_required
def criar_andar(request):
    if request.method == 'POST':
        form = AndarForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = AndarForm()

    current = _current_path(request)
    andares = Andar.objects.order_by('nome')
    rows = [
        _row(
            cols=[a.nome],
            edit_url=f"{reverse('editar_andar', args=[a.pk])}?next={current}",
            delete_url=f"{reverse('excluir_andar', args=[a.pk])}?next={current}",
        )
        for a in andares
    ]
    ctx_lista = _ctx_lista(
        titulo='Andares existentes',
        headers=['Nome'],
        rows=rows,
        vazio_msg='Não existe andar cadastrado.'
    )
    ctx = {
        'form': form,
        'titulo': 'Criar Andar',
        'next_url': current,
        'cancel_url': reverse('dashboard'),  # <- sempre dashboard na criação
        **ctx_lista
    }
    return render(request, 'form_generic.html', ctx)

@login_required
def criar_sala(request, andar_id):
    andar = get_object_or_404(Andar, pk=andar_id)

    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = SalaForm(initial={'andar': andar_id})

    current = _current_path(request)
    salas = (Sala.objects
                  .filter(andar_id=andar_id)
                  .select_related('funcao')
                  .order_by('numero', 'nome'))

    rows = [
        _row(
            cols=[s.numero, s.nome, s.funcao.nome],
            edit_url=f"{reverse('editar_sala', args=[s.pk])}?next={current}",
            delete_url=f"{reverse('excluir_sala', args=[s.pk])}?next={current}",
        )
        for s in salas
    ]
    ctx_lista = _ctx_lista(
        titulo='Salas no andar',
        headers=['Número', 'Nome', 'Funcionalidade'],
        rows=rows,
        vazio_msg='Não existe sala cadastrada neste andar.',
        subtitulo=str(andar.nome)
    )
    ctx = {
        'form': form,
        'titulo': 'Criar Sala',
        'next_url': current,
        'cancel_url': reverse('dashboard'),  # <- sempre dashboard na criação
        **ctx_lista
    }
    return render(request, 'form_generic.html', ctx)

@login_required
def criar_funcionalidade(request):
    if request.method == 'POST':
        form = FuncionalidadeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = FuncionalidadeForm()

    current = _current_path(request)
    funcionalidades = Funcionalidade.objects.order_by('nome')
    rows = [
        _row(
            cols=[f.nome],
            edit_url=f"{reverse('editar_funcionalidade', args=[f.pk])}?next={current}",
            delete_url=f"{reverse('excluir_funcionalidade', args=[f.pk])}?next={current}",
        )
        for f in funcionalidades
    ]
    ctx_lista = _ctx_lista(
        titulo='Funcionalidades existentes',
        headers=['Nome'],
        rows=rows,
        vazio_msg='Não existe funcionalidade cadastrada.'
    )
    ctx = {
        'form': form,
        'titulo': 'Criar Funcionalidade',
        'next_url': current,
        'cancel_url': reverse('dashboard'),  # <- sempre dashboard na criação
        **ctx_lista
    }
    return render(request, 'form_generic.html', ctx)

@login_required
def criar_equipamento(request):
    if request.method == 'POST':
        form = EquipamentoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = EquipamentoForm()

    current = _current_path(request)
    equipamentos = Equipamento.objects.order_by('nome')
    rows = [
        _row(
            cols=[e.nome],
            edit_url=f"{reverse('editar_equipamento', args=[e.pk])}?next={current}",
            delete_url=f"{reverse('excluir_equipamento', args=[e.pk])}?next={current}",
        )
        for e in equipamentos
    ]
    ctx_lista = _ctx_lista(
        titulo='Equipamentos existentes',
        headers=['Nome'],
        rows=rows,
        vazio_msg='Não existe equipamento cadastrado.'
    )
    ctx = {
        'form': form,
        'titulo': 'Criar Equipamento',
        'next_url': current,
        'cancel_url': reverse('dashboard'),  # <- sempre dashboard na criação
        **ctx_lista
    }
    return render(request, 'form_generic.html', ctx)

@login_required
def criar_profissional(request):
    if request.method == 'POST':
        form = ProfissionalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProfissionalForm()

    current = _current_path(request)
    profissionais = Profissional.objects.order_by('nome')
    tem_crm = hasattr(Profissional, 'crm')
    headers = ['Nome', 'Especialidade'] + (['CRM'] if tem_crm else [])
    rows = []
    for p in profissionais:
        cols = [p.nome, p.especialidade]
        if tem_crm:
            cols.append(getattr(p, 'crm', ''))
        rows.append(
            _row(
                cols=cols,
                edit_url=f"{reverse('editar_profissional', args=[p.pk])}?next={current}",
                delete_url=f"{reverse('excluir_profissional', args=[p.pk])}?next={current}",
            )
        )

    ctx_lista = _ctx_lista(
        titulo='Profissionais existentes',
        headers=headers,
        rows=rows,
        vazio_msg='Não existe profissional cadastrado.'
    )
    ctx = {
        'form': form,
        'titulo': 'Criar Profissional',
        'next_url': current,
        'cancel_url': reverse('dashboard'),  # <- sempre dashboard na criação
        **ctx_lista
    }
    return render(request, 'form_generic.html', ctx)

# ---- Quick Add Andar ----
def andar_quick_add(request):
    if request.method == 'GET':
        form = AndarForm()
        html = render_to_string('partials/andar_quick_form.html', {'form': form}, request)
        return HttpResponse(html)  # 200

    form = AndarForm(request.POST)
    if form.is_valid():
        try:
            obj = form.save()
        except IntegrityError:
            form.add_error('nome', 'Já existe um andar com esse nome.')
        else:
            resp = HttpResponse(f'<option value="{obj.id}" selected>{obj}</option>')
            resp['HX-Retarget'] = '#id_andar'
            resp['HX-Reswap'] = 'beforeend'
            resp['HX-Trigger-After-Swap'] = 'closeModal'
            return resp

    html = render_to_string('partials/andar_quick_form.html', {'form': form}, request)
    return HttpResponse(html)  # 200

# ---- Quick Add Funcionalidade ----
def func_quick_add(request):
    if request.method == 'GET':
        form = FuncionalidadeForm()
        html = render_to_string('partials/func_quick_form.html', {'form': form}, request)
        return HttpResponse(html)

    form = FuncionalidadeForm(request.POST)
    if form.is_valid():
        try:
            obj = form.save()
        except IntegrityError:
            form.add_error('nome', 'Já existe uma funcionalidade com esse nome.')
        else:
            resp = HttpResponse(f'<option value="{obj.id}" selected>{obj}</option>')
            resp['HX-Retarget'] = '#id_funcao'
            resp['HX-Reswap'] = 'beforeend'
            resp['HX-Trigger-After-Swap'] = 'closeModal'
            return resp

    html = render_to_string('partials/func_quick_form.html', {'form': form}, request)
    return HttpResponse(html)

# =========================
# CONFIG/AGENDAMENTOS
# =========================
@login_required
def configurar_profissional(request):
    profissional_id = request.GET.get('prof')

    if request.method == 'GET' and profissional_id:
        profissional = get_object_or_404(Profissional, pk=profissional_id)

        try:
            parametros = profissional.profissionalparametros
            dias = profissional.profissionaldiasatendimento_set.values_list('dia_semana', flat=True)
            equipamentos = profissional.profissionalequipamento_set.values_list('equipamento', flat=True)

            form = ParametrosProfissionalForm(initial={
                'profissional': profissional,
                'n_nc': parametros.n_nc,
                't_nc': parametros.t_nc,
                'n_ret': parametros.n_ret,
                't_ret': parametros.t_ret,
                'dias_atendimento': list(dias),
                'equipamentos': list(equipamentos),
            })

        except ProfissionalParametros.DoesNotExist:
            form = ParametrosProfissionalForm(initial={'profissional': profissional})
    elif request.method == 'POST':
        form = ParametrosProfissionalForm(request.POST)
        if form.is_valid():
            profissional = form.cleaned_data['profissional']

            ProfissionalParametros.objects.update_or_create(
                profissional=profissional,
                defaults={
                    'n_nc': form.cleaned_data['n_nc'],
                    't_nc': form.cleaned_data['t_nc'],
                    'n_ret': form.cleaned_data['n_ret'],
                    't_ret': form.cleaned_data['t_ret'],
                }
            )

            ProfissionalDiasAtendimento.objects.filter(profissional=profissional).delete()
            for dia in form.cleaned_data['dias_atendimento']:
                ProfissionalDiasAtendimento.objects.create(profissional=profissional, dia_semana=dia)

            ProfissionalEquipamento.objects.filter(profissional=profissional).delete()
            for equipamento in form.cleaned_data['equipamentos']:
                ProfissionalEquipamento.objects.create(profissional=profissional, equipamento=equipamento)

            messages.success(request, "Configurações salvas com sucesso.")
            return redirect('dashboard')
    else:
        form = ParametrosProfissionalForm()

    return render(request, 'form_generic.html', {'form': form, 'titulo': 'Configurar Profissional', 'cancel_url': reverse('dashboard')})

# =========================
# CRUD – EDITAR (honra ?next=)
# =========================
@login_required
def editar_funcionalidade(request, pk):
    funcionalidade = get_object_or_404(Funcionalidade, pk=pk)
    if request.method == 'POST':
        form = FuncionalidadeForm(request.POST, instance=funcionalidade)
        if form.is_valid():
            form.save()
            messages.success(request, "Funcionalidade atualizada com sucesso.")
            return _safe_redirect(request)
    else:
        form = FuncionalidadeForm(instance=funcionalidade)
    return render(request, 'form_generic.html', {'form': form, 'titulo': 'Editar Funcionalidade', 'next_url': request.GET.get('next')})

@login_required
def editar_equipamento(request, pk):
    equipamento = get_object_or_404(Equipamento, pk=pk)
    if request.method == 'POST':
        form = EquipamentoForm(request.POST, instance=equipamento)
        if form.is_valid():
            form.save()
            messages.success(request, "Equipamento atualizado com sucesso.")
            return _safe_redirect(request)
    else:
        form = EquipamentoForm(instance=equipamento)
    return render(request, 'form_generic.html', {'form': form, 'titulo': 'Editar Equipamento', 'next_url': request.GET.get('next')})

@login_required
def editar_profissional(request, pk):
    profissional = get_object_or_404(Profissional, pk=pk)
    if request.method == 'POST':
        form = ProfissionalForm(request.POST, instance=profissional)
        if form.is_valid():
            form.save()
            messages.success(request, "Profissional atualizado com sucesso.")
            return _safe_redirect(request)
    else:
        form = ProfissionalForm(instance=profissional)
    return render(request, 'form_generic.html', {'form': form, 'titulo': 'Editar Profissional', 'next_url': request.GET.get('next')})

@login_required
def editar_andar(request, pk):
    andar = get_object_or_404(Andar, pk=pk)
    if request.method == 'POST':
        form = AndarForm(request.POST, instance=andar)
        if form.is_valid():
            form.save()
            messages.success(request, "Andar atualizado com sucesso.")
            return _safe_redirect(request)
    else:
        form = AndarForm(instance=andar)
    return render(request, 'form_generic.html', {'form': form, 'titulo': 'Editar Andar', 'next_url': request.GET.get('next')})

@login_required
def editar_sala(request, pk):
    sala = get_object_or_404(Sala, pk=pk)
    if request.method == 'POST':
        form = SalaForm(request.POST, instance=sala)
        if form.is_valid():
            form.save()
            messages.success(request, "Sala atualizada com sucesso.")
            return _safe_redirect(request)
    else:
        form = SalaForm(instance=sala)
    return render(request, 'form_generic.html', {'form': form, 'titulo': 'Editar Sala', 'next_url': request.GET.get('next')})

# =========================
# CRUD – EXCLUIR (honra ?next=)
# =========================
@login_required
def excluir_funcionalidade(request, pk):
    funcionalidade = get_object_or_404(Funcionalidade, pk=pk)
    if request.method == 'POST':
        funcionalidade.delete()
        messages.success(request, "Funcionalidade excluída com sucesso.")
        return _safe_redirect(request)
    return render(request, 'confirm_delete.html', {
        'objeto': funcionalidade,
        'titulo': 'Excluir Funcionalidade',
        'descricao': 'Tem certeza que deseja excluir esta funcionalidade?',
        'next_url': request.GET.get('next')
    })

@login_required
def excluir_equipamento(request, pk):
    equipamento = get_object_or_404(Equipamento, pk=pk)
    if request.method == 'POST':
        equipamento.delete()
        messages.success(request, "Equipamento excluído com sucesso.")
        return _safe_redirect(request)
    return render(request, 'confirm_delete.html', {
        'objeto': equipamento,
        'titulo': 'Excluir Equipamento',
        'descricao': 'Tem certeza que deseja excluir este equipamento?',
        'next_url': request.GET.get('next')
    })

@login_required
def excluir_profissional(request, pk):
    profissional = get_object_or_404(Profissional, pk=pk)
    if request.method == 'POST':
        profissional.delete()
        messages.success(request, "Profissional excluído com sucesso.")
        return _safe_redirect(request)
    return render(request, 'confirm_delete.html', {
        'objeto': profissional,
        'titulo': 'Excluir Profissional',
        'descricao': 'Tem certeza que deseja excluir este profissional?',
        'next_url': request.GET.get('next')
    })

@login_required
def excluir_andar(request, pk):
    andar = get_object_or_404(Andar, pk=pk)
    if request.method == 'POST':
        andar.delete()
        messages.success(request, "Andar excluído com sucesso.")
        return _safe_redirect(request)
    return render(request, 'confirm_delete.html', {
        'objeto': andar,
        'titulo': 'Excluir Andar',
        'descricao': 'Tem certeza que deseja excluir este andar?',
        'next_url': request.GET.get('next')
    })

@login_required
def excluir_sala(request, pk):
    sala = get_object_or_404(Sala, pk=pk)
    if request.method == 'POST':
        sala.delete()
        messages.success(request, "Sala excluída com sucesso.")
        return _safe_redirect(request)
    return render(request, 'confirm_delete.html', {
        'objeto': sala,
        'titulo': 'Excluir Sala',
        'descricao': 'Tem certeza que deseja excluir esta sala?',
        'next_url': request.GET.get('next')
    })

# =========================
# NOVO AGENDAMENTO (Cancelar -> dashboard)
# =========================
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
        'titulo': 'Novo Agendamento',
        'cancel_url': reverse('dashboard'),  # <- sempre dashboard
    })
