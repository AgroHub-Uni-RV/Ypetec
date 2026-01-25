"""
Serializers para mentorias.
"""
from rest_framework import serializers

from apps.projetos.models import Projeto

from .models import SolicitacaoMentoria


class SolicitacaoMentoriaSerializer(serializers.ModelSerializer):
    """Serializer para leitura de solicitações de mentoria."""

    projeto_titulo = serializers.CharField(source='projeto.titulo', read_only=True)
    solicitante_nome = serializers.CharField(source='solicitante.name', read_only=True)
    solicitante_email = serializers.CharField(source='solicitante.email', read_only=True)
    mentor_nome = serializers.CharField(source='mentor.name', read_only=True, allow_null=True)

    class Meta:
        model = SolicitacaoMentoria
        fields = [
            'id',
            'projeto',
            'projeto_titulo',
            'area',
            'justificativa',
            'status',
            'solicitante',
            'solicitante_nome',
            'solicitante_email',
            'mentor',
            'mentor_nome',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'solicitante', 'status', 'mentor', 'created_at', 'updated_at'
        ]


class SolicitacaoMentoriaCreateSerializer(serializers.ModelSerializer):
    """Serializer para criar solicitação de mentoria (aluno)."""

    project_id = serializers.IntegerField(write_only=True, source='projeto_id')

    class Meta:
        model = SolicitacaoMentoria
        fields = ['project_id', 'area', 'justificativa']

    def validate_project_id(self, value):
        """Valida que o projeto existe, pertence ao usuário e está incubado."""
        user = self.context['request'].user
        try:
            projeto = Projeto.objects.get(id=value)
        except Projeto.DoesNotExist:
            raise serializers.ValidationError('Projeto não encontrado.')

        if projeto.responsavel != user:
            raise serializers.ValidationError('Você não é responsável por este projeto.')

        if projeto.status != Projeto.Status.INCUBADO:
            raise serializers.ValidationError(
                'Apenas projetos incubados podem solicitar mentoria.'
            )

        return value

    def create(self, validated_data):
        """Cria solicitação de mentoria."""
        validated_data['solicitante'] = self.context['request'].user
        return SolicitacaoMentoria.objects.create(**validated_data)


class SolicitacaoMentoriaUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualizar status da mentoria (admin)."""

    class Meta:
        model = SolicitacaoMentoria
        fields = ['status', 'mentor']

    def validate_status(self, value):
        """Valida que o status é válido."""
        valid_statuses = [s[0] for s in SolicitacaoMentoria.Status.choices]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f'Status inválido. Use: {", ".join(valid_statuses)}'
            )
        return value
