"""Filtrage multi-tenant par église (church_id)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import QuerySet # type: ignore from django.db.models


def filter_queryset_for_tenant(queryset: QuerySet, user) -> QuerySet:
    """
    Restreint le queryset à l'église de l'utilisateur.
    SuperAdmin sans église : pas de filtre (accès plateforme — à n'utiliser que sur des endpoints dédiés).
    """
    from accounts.models import UserRole

    if not user.is_authenticated:
        return queryset.none()
    if getattr(user, 'role', None) == UserRole.SUPER_ADMIN and not getattr(user, 'church_id', None):
        return queryset
    if getattr(user, 'church_id', None):
        return queryset.filter(church_id=user.church_id)
    return queryset.none()


def user_has_active_subscription(user) -> bool:
    """True si pas d'église, super-admin sans tenant, ou abonnement valide."""
    from accounts.models import UserRole
    from django.utils import timezone  # pyright: ignore[reportMissingImports]
    from churches.models import Subscription

    if not user.is_authenticated:
        return False
    if getattr(user, 'role', None) == UserRole.SUPER_ADMIN and not getattr(user, 'church_id', None):
        return True
    ch = getattr(user, 'church', None)
    if not ch:
        return False
    sub = (
        Subscription.objects.filter(church=ch, is_active=True)
        .order_by('-created_at')
        .first()
    )
    if not sub:
        return False
    return sub.is_valid_at(timezone.now().date())
