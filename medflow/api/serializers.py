from rest_framework import serializers

from medflow.models import AgendamentoSala


class AgendamentoPublicoSerializer(serializers.ModelSerializer):
    """
    Serializer público para agendamentos.
    Retorna apenas informações básicas: horário, sala, profissional, especialidade.
    """
    sala_nome = serializers.CharField(source='sala.nome', read_only=True)
    sala_numero = serializers.IntegerField(source='sala.numero', read_only=True)
    profissional_nome = serializers.CharField(source='profissional.nome', read_only=True)
    especialidade = serializers.CharField(source='profissional.especialidade', read_only=True)
    
    class Meta:
        model = AgendamentoSala
        fields = [
            'id',
            'data_agendamento',
            'horario_inicio',
            'horario_final',
            'sala_numero',
            'sala_nome',
            'profissional_nome',
            'especialidade',
        ]
        read_only_fields = fields


class AgendamentoDataHorariosSerializer(serializers.Serializer):
    """
    Serializer customizado para retornar dados e horários com agendamentos.
    """
    data = serializers.DateField()
    horários = serializers.ListField(
        child=serializers.DictField(),
        help_text="Lista de horários agendados para a data"
    )
