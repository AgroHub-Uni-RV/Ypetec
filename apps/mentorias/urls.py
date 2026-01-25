"""
URLs do app mentorias.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SolicitacaoMentoriaViewSet

router = DefaultRouter()
router.register('mentorship-requests', SolicitacaoMentoriaViewSet, basename='mentoria')

urlpatterns = [
    path('', include(router.urls)),
]
