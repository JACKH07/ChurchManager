from rest_framework import viewsets, status  # pyright: ignore[reportMissingImports]
from rest_framework.decorators import action  # pyright: ignore[reportMissingImports]
from rest_framework.response import Response  # pyright: ignore[reportMissingImports]
from drf_spectacular.utils import extend_schema  # pyright: ignore[reportMissingImports]

from .models import Notification
from .serializers import NotificationSerializer
from accounts.permissions import IsAuthenticated


@extend_schema(tags=['notifications'])
class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(destinataire=self.request.user)

    @action(detail=False, methods=['post'])
    def marquer_toutes_lues(self, request):
        self.get_queryset().update(est_lue=True)
        return Response({'detail': 'Toutes les notifications marquées comme lues.'})

    @action(detail=True, methods=['post'])
    def marquer_lue(self, request, pk=None):
        notif = self.get_object()
        notif.est_lue = True
        notif.save()
        return Response(NotificationSerializer(notif).data)

    @action(detail=False, methods=['get'])
    def non_lues(self, request):
        qs = self.get_queryset().filter(est_lue=False)
        return Response({'count': qs.count(), 'notifications': NotificationSerializer(qs[:10], many=True).data})
