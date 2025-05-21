from django.urls import path
from .views import configurar_profissional, criar_andar, criar_sala, criar_profissional, criar_funcionalidade, editar_funcionalidade, excluir_funcionalidade, criar_equipamento, editar_equipamento, excluir_equipamento
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('agendamentos/', views.visualizar_agendamentos, name='visualizar_agendamentos'),
    path('agendamentos/lista/', views.lista_agendamentos, name='lista_agendamentos'),
    path('agendar-sala/<int:sala_id>/', views.agendar_sala, name='agendar_sala'),    
    # CRUD de Andar
    path('criar-andar/', criar_andar, name='criar_andar'),    
    path('andar/editar/<int:pk>/', views.editar_andar, name='editar_andar'),
    path('andar/excluir/<int:pk>/', views.excluir_andar, name='excluir_andar'),
    # CRUD de Funcionalidade
    path('criar-funcionalidade/', criar_funcionalidade, name='criar_funcionalidade'),    
    path('funcionalidade/editar/<int:pk>/', editar_funcionalidade, name='editar_funcionalidade'),
    path('funcionalidade/excluir/<int:pk>/', excluir_funcionalidade, name='excluir_funcionalidade'),
    # CRUD de Equipamento
    path('criar-equipamento/', criar_equipamento, name='criar_equipamento'),    
    path('equipamento/editar/<int:pk>/', editar_equipamento, name='editar_equipamento'),
    path('equipamento/excluir/<int:pk>/', excluir_equipamento, name='excluir_equipamento'),
    # CRUD de Sala
    path('criar-sala/<int:andar_id>/', criar_sala, name='criar_sala'),
    path('sala/editar/<int:pk>/', views.editar_sala, name='editar_sala'),
    path('sala/excluir/<int:pk>/', views.excluir_sala, name='excluir_sala'),
    # CRUD de Profissional
    path('configurar-profissional/', configurar_profissional, name='configurar_profissional'),
    path('criar-profissional/', criar_profissional, name='criar_profissional'),
    path('profissional/editar/<int:pk>/', views.editar_profissional, name='editar_profissional'),
    path('profissional/excluir/<int:pk>/', views.excluir_profissional, name='excluir_profissional'),
    path('agendamento/novo/', views.novo_agendamento, name='novo_agendamento'),
]
