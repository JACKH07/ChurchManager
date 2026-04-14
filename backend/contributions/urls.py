from django.urls import path, include # type: ignore from django.urls
from rest_framework.routers import DefaultRouter # type: ignore from rest_framework.routers
from .views import CotisationViewSet, RecuViewSet, ObjectifCotisationViewSet # type: ignore from local app

router = DefaultRouter()
router.register('cotisations', CotisationViewSet, basename='cotisations')
router.register('recus', RecuViewSet, basename='recus')
router.register('objectifs', ObjectifCotisationViewSet, basename='objectifs')

urlpatterns = [
    path('', include(router.urls)),
]
