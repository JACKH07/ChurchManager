from django.urls import path, include # type: ignore from django.urls
from rest_framework.routers import DefaultRouter # type: ignore from rest_framework.routers
from .views import EvenementViewSet, AnnonceViewSet

router = DefaultRouter()
router.register('evenements', EvenementViewSet, basename='evenements')
router.register('annonces', AnnonceViewSet, basename='annonces')

urlpatterns = [
    path('', include(router.urls)),
]
