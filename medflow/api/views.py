from datetime import datetime, timedelta

from django.core.cache import cache
from django.db.models import F, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from medflow.models import AgendamentoSala

from .serializers import (AgendamentoDataHorariosSerializer,
                          AgendamentoPublicoSerializer)


class PublicAgendamentoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API pública READ-ONLY de agendamentos.
    Retorna horários agendados por data.
    
    Endpoints:
    - GET /api/public/agendamentos/ - Lista todos agendamentos
    - GET /api/public/agendamentos/{id}/ - Detalhe do agendamento
    - GET /api/public/agendamentos/calendar/disponibilidade/ - Horários por data
    """
    queryset = AgendamentoSala.objects.select_related('sala', 'profissional').all()
    serializer_class = AgendamentoPublicoSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    filterset_fields = ['data_agendamento', 'sala']

    def get_queryset(self):
        """Retorna apenas agendamentos futuros ou de hoje."""
        hoje = datetime.now().date()
        return super().get_queryset().filter(data_agendamento__gte=hoje).order_by('data_agendamento', 'horario_inicio')

    @action(detail=False, methods=['get'], url_path='calendar/disponibilidade')
    def calendar_disponibilidade(self, request):
        """
        Retorna dias e horários com agendamentos.
        
        Query params:
        - data_inicio: YYYY-MM-DD (default: hoje)
        - data_fim: YYYY-MM-DD (default: hoje + 30 dias)
        - sala_id: filtrar por sala (opcional)
        
        Response:
        {
            "datas": [
                {
                    "data": "2026-04-14",
                    "horarios": [
                        {
                            "inicio": "09:00",
                            "fim": "10:00",
                            "sala": "Sala 101",
                            "profissional": "Dr. Silva",
                            "especialidade": "Cardiologia"
                        }
                    ]
                }
            ]
        }
        """
        # Cache key
        cache_key = f"agendamentos:calendario:{request.GET.urlencode()}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Datas
        hoje = datetime.now().date()
        data_inicio = request.query_params.get('data_inicio', str(hoje))
        data_fim = request.query_params.get('data_fim', str(hoje + timedelta(days=30)))
        
        try:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"erro": "Datas inválidas. Use formato YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Filter
        agendamentos = self.get_queryset().filter(
            data_agendamento__range=[data_inicio, data_fim]
        )

        sala_id = request.query_params.get('sala_id')
        if sala_id:
            agendamentos = agendamentos.filter(sala_id=sala_id)

        # Agrupar por data
        dados_por_data = {}
        for agendamento in agendamentos:
            data_str = str(agendamento.data_agendamento)
            if data_str not in dados_por_data:
                dados_por_data[data_str] = []

            dados_por_data[data_str].append({
                'inicio': agendamento.horario_inicio.strftime('%H:%M'),
                'fim': agendamento.horario_final.strftime('%H:%M'),
                'sala': agendamento.sala.nome,
                'sala_numero': agendamento.sala.numero,
                'profissional': agendamento.profissional.nome,
                'especialidade': agendamento.profissional.especialidade.nome,
            })

        # Montar resposta
        resposta = {
            'datas': [
                {
                    'data': data,
                    'horarios': horarios
                }
                for data, horarios in sorted(dados_por_data.items())
            ],
            'periodo': {
                'inicio': str(data_inicio),
                'fim': str(data_fim),
            }
        }

        # Cache por 1 hora
        cache.set(cache_key, resposta, timeout=3600)
        
        return Response(resposta)

    @action(detail=False, methods=['get'], url_path='dias-com-agendamentos')
    def dias_com_agendamentos(self, request):
        """
        Retorna apenas DATAS que têm agendamentos (sem horários).
        Útil para calendários de disponibilidade.
        
        Query params:
        - data_inicio: YYYY-MM-DD
        - data_fim: YYYY-MM-DD
        - sala_id: opcional
        
        Response:
        {
            "datas": ["2026-04-14", "2026-04-15", ...],
            "total": 15
        }
        """
        cache_key = f"agendamentos:dias:{request.GET.urlencode()}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        hoje = datetime.now().date()
        data_inicio = request.query_params.get('data_inicio', str(hoje))
        data_fim = request.query_params.get('data_fim', str(hoje + timedelta(days=30)))

        try:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"erro": "Datas inválidas. Use formato YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )

        agendamentos = self.get_queryset().filter(
            data_agendamento__range=[data_inicio, data_fim]
        ).values_list('data_agendamento', flat=True).distinct().order_by('data_agendamento')

        sala_id = request.query_params.get('sala_id')
        if sala_id:
            agendamentos = agendamentos.filter(sala_id=sala_id)

        datas_str = [str(d) for d in agendamentos]

        resposta = {
            'datas': datas_str,
            'total': len(datas_str),
            'periodo': {
                'inicio': str(data_inicio),
                'fim': str(data_fim),
            }
        }

        cache.set(cache_key, resposta, timeout=3600)
        return Response(resposta)
