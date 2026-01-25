"""
URLs do app projetos.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProjetoViewSet, SubmissaoViewSet

router = DefaultRouter()
router.register('projects', ProjetoViewSet, basename='projeto')
router.register('submissions', SubmissaoViewSet, basename='submissao')

urlpatterns = [
    path('', include(router.urls)),

    # Rotas alternativas para compatibilidade com frontend
    path(
        'students/me/projects',
        ProjetoViewSet.as_view({'get': 'my_projects'}),
        name='my-projects'
    ),
    path(
        'students/me/incubated-projects',
        ProjetoViewSet.as_view({'get': 'incubated'}),
        name='incubated-projects'
    ),
]
