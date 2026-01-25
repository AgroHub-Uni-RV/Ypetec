"""
Configuração de URLs do projeto YpeTec.

A rota `api/` contém todas as rotas da API REST.
As demais rotas são para templates (MVT).
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),

    # ========== ROTAS DE TEMPLATES (MVT) ==========
    # Home
    path('', include('apps.home.urls')),

    # Autenticação (templates)
    path('auth/', include('apps.contas.urls_templates', namespace='contas')),

    # Editais (templates)
    path('editais/', include('apps.editais.urls_templates', namespace='editais')),

    # Projetos (templates)
    path('projetos/', include('apps.projetos.urls_templates', namespace='projetos')),

    # Avaliações (templates)
    path('avaliacoes/', include('apps.avaliacoes.urls_templates', namespace='avaliacoes')),

    # Mentorias (templates)
    path('mentorias/', include('apps.mentorias.urls_templates', namespace='mentorias')),

    # Publicações (templates)
    path('publicacoes/', include('apps.publicacoes.urls_templates', namespace='publicacoes')),

    # ========== ROTAS DA API REST ==========
    path('api/', include('apps.contas.urls')),
    path('api/', include('apps.editais.urls')),
    path('api/', include('apps.projetos.urls')),
    path('api/', include('apps.avaliacoes.urls')),
    path('api/', include('apps.mentorias.urls')),
    path('api/', include('apps.publicacoes.urls')),
]

# Servir arquivos estáticos e de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
