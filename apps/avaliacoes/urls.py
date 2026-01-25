"""
URLs do app avaliacoes.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AvaliacaoViewSet

router = DefaultRouter()
router.register('evaluations', AvaliacaoViewSet, basename='avaliacao')

urlpatterns = [
    path('', include(router.urls)),
]
