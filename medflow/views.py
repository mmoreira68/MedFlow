from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Andar, Sala, AgendamentoSala
from .forms import AgendamentoSalaForm
from datetime import date

# Página inicial
def home(request):
    return render(request, 'home.html')

# Página pública de agendamentos do dia
def visualizar_agendamentos(request):
    hoje = date.today()
    agendamentos = AgendamentoSala.objects.filter(data_agendamento=hoje)
    return render(request, 'agendamentos_publico.html', {'agendamentos': agendamentos})

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

# Dashboard de gestão
@login_required
def dashboard(request):
    andares = Andar.objects.prefetch_related('sala_set').all()
    return render(request, 'dashboard.html', {'andares': andares})

# Agendar uma sala
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
