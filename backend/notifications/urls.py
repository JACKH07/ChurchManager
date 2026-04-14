from django.urls import path, include  # pyright: ignore[reportMissingImports]
from rest_framework.routers import DefaultRouter  # pyright: ignore[reportMissingImports]
from .views import NotificationViewSet

router = DefaultRouter()
router.register('notifications', NotificationViewSet, basename='notifications')

urlpatterns = [
    path('', include(router.urls)),
]
