from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home principal
    path('agendamentos/', views.visualizar_agendamentos, name='visualizar_agendamentos'),  # Página pública
    path('login/', views.login_view, name='login'),  # Tela de login
    path('logout/', views.logout_view, name='logout'),  # Logout
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard
    path('agendar-sala/<int:sala_id>/', views.agendar_sala, name='agendar_sala'),  # Agendar sala
]
