from django.urls import path, include # type: ignore from django.urls
from rest_framework.routers import DefaultRouter # type: ignore from rest_framework.routers
from .views import FideleViewSet, MinistereViewSet, TransfertFideleViewSet # type: ignore from local app

router = DefaultRouter()
router.register('fideles', FideleViewSet, basename='fideles')
router.register('ministeres', MinistereViewSet, basename='ministeres')
router.register('transferts', TransfertFideleViewSet, basename='transferts')

urlpatterns = [
    path('', include(router.urls)),
]
