from rest_framework import viewsets, status # type: ignore from rest_framework          
from rest_framework.decorators import action # type: ignore from rest_framework.decorators
from rest_framework.response import Response # type: ignore from rest_framework.response
from rest_framework.permissions import IsAuthenticated  # type: ignore from rest_framework.permissions

from common.tenant import filter_queryset_for_tenant
from drf_spectacular.utils import extend_schema # type: ignore from drf_spectacular.utils

from .models import Notification
from .serializers import NotificationSerializer


@extend_schema(tags=['notifications'])
class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        qs = Notification.objects.filter(destinataire=self.request.user).order_by('-created_at')
        return filter_queryset_for_tenant(qs, self.request.user)

    def perform_create(self, serializer):
        u = self.request.user
        if getattr(u, 'church_id', None):
            serializer.save(destinataire=u, church=u.church)
        else:
            serializer.save(destinataire=u)

    @action(detail=False, methods=['post'])
    def marquer_toutes_lues(self, request):
        updated = self.get_queryset().filter(est_lue=False).update(est_lue=True)
        return Response({'detail': f'{updated} notification(s) marquée(s) comme lues.'})

    @action(detail=True, methods=['post'])
    def marquer_lue(self, request, pk=None):
        notif = self.get_object()
        notif.est_lue = True
        notif.save()
        return Response(NotificationSerializer(notif).data)

    @action(detail=False, methods=['get'])
    def non_lues(self, request):
        qs = self.get_queryset().filter(est_lue=False)
        return Response({
            'count': qs.count(),
            'notifications': NotificationSerializer(qs[:10], many=True).data,
        })
