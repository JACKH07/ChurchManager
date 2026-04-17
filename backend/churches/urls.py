from django.urls import path, include # type: ignore from django.urls
from rest_framework.routers import DefaultRouter # type: ignore from rest_framework.routers

from .views import ChurchViewSet, SubscriptionViewSet, PlatformChurchViewSet

router = DefaultRouter()
router.register('my-church', ChurchViewSet, basename='my-church')
router.register('subscriptions', SubscriptionViewSet, basename='subscriptions')
router.register('platform/churches', PlatformChurchViewSet, basename='platform-churches')

urlpatterns = [
    path('', include(router.urls)),
]
