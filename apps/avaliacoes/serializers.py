"""
Serializers para avaliações.
"""
from rest_framework import serializers

from apps.projetos.models import Projeto, Submissao

from .models import Avaliacao


class AvaliacaoSerializer(serializers.ModelSerializer):
    """Serializer para leitura de avaliações."""

    avaliador_nome = serializers.CharField(source='avaliador.name', read_only=True)
    submissao_projeto = serializers.CharField(source='submissao.projeto.titulo', read_only=True)

    class Meta:
        model = Avaliacao
        fields = [
            'id',
            'submissao',
            'submissao_projeto',
            'avaliador',
            'avaliador_nome',
            'resultado',
            'comentarios',
            'avaliado_em',
        ]
        read_only_fields = ['id', 'avaliador', 'avaliado_em']


class AvaliacaoCreateSerializer(serializers.ModelSerializer):
    """Serializer para criar avaliação (admin)."""

    submission_id = serializers.IntegerField(write_only=True)
    status = serializers.ChoiceField(
        choices=Avaliacao.Resultado.choices,
        write_only=True,
    )
    comments = serializers.CharField(write_only=True)

    class Meta:
        model = Avaliacao
        fields = ['submission_id', 'status', 'comments']

    def validate_submission_id(self, value):
        """Valida que a submissão existe."""
        try:
            Submissao.objects.get(id=value)
        except Submissao.DoesNotExist:
            raise serializers.ValidationError('Submissão não encontrada.')
        return value

    def create(self, validated_data):
        """Cria avaliação e atualiza status da submissão/projeto."""
        submissao = Submissao.objects.get(id=validated_data['submission_id'])
        resultado = validated_data['status']

        # Criar avaliação
        avaliacao = Avaliacao.objects.create(
            submissao=submissao,
            avaliador=self.context['request'].user,
            resultado=resultado,
            comentarios=validated_data['comments'],
        )

        # Atualizar status da submissão
        status_map = {
            Avaliacao.Resultado.APROVADO: Submissao.Status.APROVADA,
            Avaliacao.Resultado.REPROVADO: Submissao.Status.REPROVADA,
            Avaliacao.Resultado.NECESSITA_AJUSTES: Submissao.Status.AJUSTES_SOLICITADOS,
        }
        submissao.status = status_map.get(resultado, submissao.status)
        submissao.save(update_fields=['status'])

        # Atualizar status do projeto
        projeto = submissao.projeto
        projeto_status_map = {
            Avaliacao.Resultado.APROVADO: Projeto.Status.APROVADO,
            Avaliacao.Resultado.REPROVADO: Projeto.Status.REPROVADO,
            Avaliacao.Resultado.NECESSITA_AJUSTES: Projeto.Status.AJUSTES,
        }
        projeto.status = projeto_status_map.get(resultado, projeto.status)
        projeto.save(update_fields=['status', 'updated_at'])

        return avaliacao
