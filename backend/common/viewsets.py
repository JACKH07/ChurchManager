"""ViewSets avec isolation tenant."""

from __future__ import annotations

from rest_framework import viewsets # type: ignore from rest_framework

from common.tenant import filter_queryset_for_tenant


class TenantScopedModelViewSet(viewsets.ModelViewSet):
    """
    Filtre automatiquement par request.user.church.
    perform_create assigne church si l'utilisateur a une église.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        if getattr(self, 'swagger_fake_view', False):
            return qs
        return filter_queryset_for_tenant(qs, self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, 'church_id', None):
            serializer.save(church=user.church)
        else:
            serializer.save()


class TenantScopedReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        qs = super().get_queryset()
        if getattr(self, 'swagger_fake_view', False):
            return qs
        return filter_queryset_for_tenant(qs, self.request.user)
