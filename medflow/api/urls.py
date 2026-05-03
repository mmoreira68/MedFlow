from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PublicAgendamentoViewSet

router = DefaultRouter()
router.register(r'agendamentos', PublicAgendamentoViewSet, basename='agendamento-publico')

urlpatterns = [
    path('', include(router.urls)),
]
