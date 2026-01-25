"""
URLs do app editais.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EditalViewSet

router = DefaultRouter()
router.register('calls', EditalViewSet, basename='edital')

urlpatterns = [
    path('', include(router.urls)),
]
