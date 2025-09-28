from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Agendamentos
    path('agendamentos/', views.visualizar_agendamentos, name='visualizar_agendamentos'),
    path('agendamentos/lista/', views.lista_agendamentos, name='lista_agendamentos'),
    path('agendar-sala/<int:sala_id>/', views.agendar_sala, name='agendar_sala'),
    path('agendamento/novo/', views.novo_agendamento, name='novo_agendamento'),

    # CRUD de Andar
    path('criar-andar/', views.criar_andar, name='criar_andar'),
    path('andar/editar/<int:pk>/', views.editar_andar, name='editar_andar'),
    path('andar/excluir/<int:pk>/', views.excluir_andar, name='excluir_andar'),

    # CRUD de Funcionalidade
    path('criar-funcionalidade/', views.criar_funcionalidade, name='criar_funcionalidade'),
    path('funcionalidade/editar/<int:pk>/', views.editar_funcionalidade, name='editar_funcionalidade'),
    path('funcionalidade/excluir/<int:pk>/', views.excluir_funcionalidade, name='excluir_funcionalidade'),

    # CRUD de Equipamento
    path('criar-equipamento/', views.criar_equipamento, name='criar_equipamento'),
    path('equipamento/editar/<int:pk>/', views.editar_equipamento, name='editar_equipamento'),
    path('equipamento/excluir/<int:pk>/', views.excluir_equipamento, name='excluir_equipamento'),

    # CRUD de Sala
    path('criar-sala/<int:andar_id>/', views.criar_sala, name='criar_sala'),
    path('sala/editar/<int:pk>/', views.editar_sala, name='editar_sala'),
    path('sala/excluir/<int:pk>/', views.excluir_sala, name='excluir_sala'),

    # CRUD de Profissional
    path('configurar-profissional/', views.configurar_profissional, name='configurar_profissional'),
    path('criar-profissional/', views.criar_profissional, name='criar_profissional'),
    path('profissional/editar/<int:pk>/', views.editar_profissional, name='editar_profissional'),
    path('profissional/excluir/<int:pk>/', views.excluir_profissional, name='excluir_profissional'),

    # Quick-add andar-função (HTMX)
    path('andar/quick-add/', views.andar_quick_add, name='andar_quick_add'),
    path('funcionalidade/quick-add/', views.func_quick_add, name='func_quick_add'),
]
