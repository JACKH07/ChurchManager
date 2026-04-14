from django.urls import path, include # type: ignore from django.urls
from rest_framework.routers import DefaultRouter # type: ignore from rest_framework.routers
from .views import NationalViewSet, RegionViewSet, DistrictViewSet, ParoisseViewSet, EgliseLocaleViewSet

router = DefaultRouter()
router.register('national', NationalViewSet, basename='national')
router.register('regions', RegionViewSet, basename='regions')
router.register('districts', DistrictViewSet, basename='districts')
router.register('paroisses', ParoisseViewSet, basename='paroisses')
router.register('eglises', EgliseLocaleViewSet, basename='eglises')

urlpatterns = [
    path('', include(router.urls)),
]
