from django.urls import path

from .views import visualizar_agendamentos

urlpatterns = [
    path("", visualizar_agendamentos, name="visualizar_agendamentos"),
]