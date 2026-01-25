"""
Serializers para editais.
"""
from rest_framework import serializers

from .models import Edital


class EditalSerializer(serializers.ModelSerializer):
    """Serializer para leitura de editais."""

    criado_por_nome = serializers.CharField(source='criado_por.name', read_only=True)
    esta_aberto = serializers.BooleanField(read_only=True)

    class Meta:
        model = Edital
        fields = [
            'id',
            'titulo',
            'descricao',
            'inicio',
            'fim',
            'status',
            'criado_por',
            'criado_por_nome',
            'esta_aberto',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'criado_por', 'criado_por_nome', 'created_at', 'updated_at']


class EditalCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de editais (admin)."""

    class Meta:
        model = Edital
        fields = ['id', 'titulo', 'descricao', 'inicio', 'fim']
        read_only_fields = ['id']

    def validate(self, attrs):
        """Valida que data de início é anterior à data de fim."""
        if attrs.get('inicio') and attrs.get('fim'):
            if attrs['inicio'] >= attrs['fim']:
                raise serializers.ValidationError({
                    'fim': 'A data de encerramento deve ser posterior à data de início.'
                })
        return attrs

    def create(self, validated_data):
        """Cria edital com status PUBLICADO e criado_por do request."""
        validated_data['criado_por'] = self.context['request'].user
        validated_data['status'] = Edital.Status.PUBLICADO
        return super().create(validated_data)


class EditalListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem."""

    class Meta:
        model = Edital
        fields = [
            'id',
            'titulo',
            'descricao',
            'inicio',
            'fim',
            'criado_por',
        ]
