"""
Serializers para publicações.
"""
from rest_framework import serializers

from apps.projetos.models import Projeto

from .models import Publicacao


class PublicacaoSerializer(serializers.ModelSerializer):
    """Serializer para leitura de publicações."""

    projeto_titulo = serializers.CharField(source='projeto.titulo', read_only=True)
    projeto_area = serializers.CharField(source='projeto.area', read_only=True)
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Publicacao
        fields = [
            'id',
            'projeto',
            'projeto_titulo',
            'projeto_area',
            'logo',
            'logo_url',
            'descricao',
            'destaque',
            'ativo',
            'publicado_por',
            'publicado_em',
        ]
        read_only_fields = ['id', 'publicado_por', 'publicado_em']

    def get_logo_url(self, obj):
        """Retorna URL completa do logo."""
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None


class PublicacaoCreateSerializer(serializers.ModelSerializer):
    """Serializer para criar publicação (admin)."""

    project_id = serializers.IntegerField(write_only=True)
    public_description = serializers.CharField(write_only=True)

    class Meta:
        model = Publicacao
        fields = ['project_id', 'logo', 'public_description']

    def validate_project_id(self, value):
        """Valida que o projeto existe e está aprovado."""
        try:
            projeto = Projeto.objects.get(id=value)
        except Projeto.DoesNotExist:
            raise serializers.ValidationError('Projeto não encontrado.')

        if projeto.status not in [Projeto.Status.APROVADO, Projeto.Status.INCUBADO]:
            raise serializers.ValidationError(
                'Apenas projetos aprovados ou incubados podem ser publicados.'
            )

        # Verifica se já existe publicação
        if Publicacao.objects.filter(projeto=projeto).exists():
            raise serializers.ValidationError('Este projeto já possui uma publicação.')

        return value

    def create(self, validated_data):
        """Cria publicação e atualiza status do projeto."""
        projeto = Projeto.objects.get(id=validated_data['project_id'])

        publicacao = Publicacao.objects.create(
            projeto=projeto,
            logo=validated_data['logo'],
            descricao=validated_data['public_description'],
            publicado_por=self.context['request'].user,
        )

        # Atualiza status do projeto para INCUBADO
        if projeto.status == Projeto.Status.APROVADO:
            projeto.status = Projeto.Status.INCUBADO
            projeto.save(update_fields=['status', 'updated_at'])

        return publicacao


class PublicacaoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para vitrine pública."""

    projeto_titulo = serializers.CharField(source='projeto.titulo', read_only=True)
    projeto_area = serializers.CharField(source='projeto.area', read_only=True)
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Publicacao
        fields = [
            'id',
            'projeto_titulo',
            'projeto_area',
            'logo_url',
            'descricao',
            'publicado_em',
        ]

    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None
