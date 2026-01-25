"""
Serializers para projetos, equipe e submissões.
"""
from rest_framework import serializers

from apps.editais.models import Edital

from .models import MembroEquipe, Projeto, RelatorioProgresso, Submissao


class MembroEquipeSerializer(serializers.ModelSerializer):
    """Serializer para membros da equipe."""

    class Meta:
        model = MembroEquipe
        fields = ['id', 'nome', 'email', 'funcao', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProjetoSerializer(serializers.ModelSerializer):
    """Serializer para leitura de projetos."""

    responsavel_nome = serializers.CharField(source='responsavel.name', read_only=True)
    membros = MembroEquipeSerializer(many=True, read_only=True)

    class Meta:
        model = Projeto
        fields = [
            'id',
            'titulo',
            'resumo',
            'area',
            'status',
            'responsavel',
            'responsavel_nome',
            'membros',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'status', 'responsavel', 'created_at', 'updated_at']


class ProjetoCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de projetos (aluno)."""

    team = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        write_only=True,
    )

    class Meta:
        model = Projeto
        fields = ['id', 'titulo', 'resumo', 'area', 'team']
        read_only_fields = ['id']

    def create(self, validated_data):
        """Cria projeto com membros da equipe."""
        team_data = validated_data.pop('team', [])
        validated_data['responsavel'] = self.context['request'].user

        projeto = Projeto.objects.create(**validated_data)

        # Criar membros da equipe
        for membro in team_data:
            if membro.get('member_name') and membro.get('role_in_team'):
                MembroEquipe.objects.create(
                    projeto=projeto,
                    nome=membro['member_name'],
                    email=membro.get('member_email', ''),
                    funcao=membro['role_in_team'],
                )

        return projeto


class ProjetoListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de projetos do aluno."""

    # Campos calculados da última submissão/avaliação
    call_title = serializers.SerializerMethodField()
    status_label = serializers.SerializerMethodField()
    submission_id = serializers.SerializerMethodField()
    evaluation_status = serializers.SerializerMethodField()

    class Meta:
        model = Projeto
        fields = [
            'id',
            'titulo',
            'area',
            'status',
            'call_title',
            'status_label',
            'submission_id',
            'evaluation_status',
        ]

    def get_call_title(self, obj):
        """Retorna título do último edital submetido."""
        ultima_submissao = obj.submissoes.order_by('-submetido_em').first()
        if ultima_submissao:
            return ultima_submissao.edital.titulo
        return '—'

    def get_submission_id(self, obj):
        """Retorna ID da última submissão."""
        ultima_submissao = obj.submissoes.order_by('-submetido_em').first()
        return ultima_submissao.id if ultima_submissao else None

    def get_evaluation_status(self, obj):
        """Retorna status da última avaliação."""
        ultima_submissao = obj.submissoes.order_by('-submetido_em').first()
        if ultima_submissao:
            ultima_avaliacao = ultima_submissao.avaliacoes.order_by('-avaliado_em').first()
            if ultima_avaliacao:
                return ultima_avaliacao.resultado
        return None

    def get_status_label(self, obj):
        """Retorna label amigável do status."""
        # Status do projeto prevalece
        if obj.status == Projeto.Status.INCUBADO:
            return 'Incubado'
        if obj.status == Projeto.Status.DESLIGADO:
            return 'Desligado'

        # Verifica última submissão
        ultima_submissao = obj.submissoes.order_by('-submetido_em').first()
        if ultima_submissao:
            # Verifica última avaliação
            ultima_avaliacao = ultima_submissao.avaliacoes.order_by('-avaliado_em').first()
            if ultima_avaliacao:
                if ultima_avaliacao.resultado == 'APROVADO':
                    return 'Aprovado'
                if ultima_avaliacao.resultado == 'REPROVADO':
                    return 'Reprovado'
                if ultima_avaliacao.resultado == 'NECESSITA_AJUSTES':
                    return 'Necessita ajustes'

            # Status da submissão
            status_map = {
                'EM_AVALIACAO': 'Em avaliação',
                'AJUSTES_SOLICITADOS': 'Ajustes solicitados',
                'APROVADA': 'Aprovada (aguardando publicação)',
                'REPROVADA': 'Reprovada',
                'ENVIADA': 'Enviada',
            }
            return status_map.get(ultima_submissao.status, ultima_submissao.status)

        # Status do projeto
        status_map = {
            'SUBMETIDO': 'Submetido',
            'AJUSTES': 'Ajustes',
            'APROVADO': 'Aprovado',
            'REPROVADO': 'Reprovado',
        }
        return status_map.get(obj.status, 'Rascunho')


class SubmissaoSerializer(serializers.ModelSerializer):
    """Serializer para submissões."""

    projeto_titulo = serializers.CharField(source='projeto.titulo', read_only=True)
    projeto_resumo = serializers.CharField(source='projeto.resumo', read_only=True)
    projeto_area = serializers.CharField(source='projeto.area', read_only=True)
    projeto_status = serializers.CharField(source='projeto.status', read_only=True)
    edital_titulo = serializers.CharField(source='edital.titulo', read_only=True)
    evaluation_status = serializers.SerializerMethodField()
    evaluation_comments = serializers.SerializerMethodField()
    evaluation_date = serializers.SerializerMethodField()

    class Meta:
        model = Submissao
        fields = [
            'id',
            'projeto',
            'projeto_titulo',
            'projeto_resumo',
            'projeto_area',
            'projeto_status',
            'edital',
            'edital_titulo',
            'status',
            'submetido_em',
            'evaluation_status',
            'evaluation_comments',
            'evaluation_date',
        ]
        read_only_fields = ['id', 'status', 'submetido_em']

    def get_evaluation_status(self, obj):
        ultima = obj.avaliacoes.order_by('-avaliado_em').first()
        return ultima.resultado if ultima else None

    def get_evaluation_comments(self, obj):
        ultima = obj.avaliacoes.order_by('-avaliado_em').first()
        return ultima.comentarios if ultima else None

    def get_evaluation_date(self, obj):
        ultima = obj.avaliacoes.order_by('-avaliado_em').first()
        return ultima.avaliado_em if ultima else None


class SubmissaoCreateSerializer(serializers.Serializer):
    """Serializer para criar submissão."""

    project_id = serializers.IntegerField()
    call_id = serializers.IntegerField()

    def validate_project_id(self, value):
        """Valida que o projeto existe e pertence ao usuário."""
        user = self.context['request'].user
        try:
            projeto = Projeto.objects.get(id=value)
        except Projeto.DoesNotExist:
            raise serializers.ValidationError('Projeto não encontrado.')

        # BUG FIX: Verifica ownership (faltava no Node.js)
        if projeto.responsavel != user:
            raise serializers.ValidationError('Você não é responsável por este projeto.')

        if not projeto.pode_submeter:
            raise serializers.ValidationError(
                f'Projeto com status "{projeto.status}" não pode ser submetido.'
            )

        return value

    def validate_call_id(self, value):
        """Valida que o edital existe e está aberto."""
        try:
            edital = Edital.objects.get(id=value)
        except Edital.DoesNotExist:
            raise serializers.ValidationError('Edital não encontrado.')

        if not edital.esta_aberto:
            raise serializers.ValidationError('Este edital não está aberto para submissões.')

        return value

    def validate(self, attrs):
        """Valida que não há submissão duplicada."""
        if Submissao.objects.filter(
            projeto_id=attrs['project_id'],
            edital_id=attrs['call_id']
        ).exists():
            raise serializers.ValidationError({
                'detail': 'Este projeto já foi submetido a este edital.'
            })
        return attrs

    def create(self, validated_data):
        """Cria a submissão."""
        submissao = Submissao.objects.create(
            projeto_id=validated_data['project_id'],
            edital_id=validated_data['call_id'],
        )

        # Atualiza status do projeto
        projeto = submissao.projeto
        projeto.status = Projeto.Status.SUBMETIDO
        projeto.save(update_fields=['status', 'updated_at'])

        return submissao


class RelatorioProgressoSerializer(serializers.ModelSerializer):
    """Serializer para relatórios de progresso."""

    autor_nome = serializers.CharField(source='autor.name', read_only=True)

    class Meta:
        model = RelatorioProgresso
        fields = [
            'id',
            'projeto',
            'periodo',
            'conteudo',
            'autor',
            'autor_nome',
            'created_at',
        ]
        read_only_fields = ['id', 'autor', 'created_at']
