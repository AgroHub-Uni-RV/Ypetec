"""
URLs do app publicacoes.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PublicacaoViewSet

router = DefaultRouter()
router.register('publications', PublicacaoViewSet, basename='publicacao')

urlpatterns = [
    path('', include(router.urls)),
]
