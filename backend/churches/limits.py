"""Limites fonctionnelles selon le plan d'abonnement."""

from __future__ import annotations

from django.utils import timezone # type: ignore from django.utils

from members.models import Fidele


PLAN_MAX_FIDELES = {
    'free': 200,
    'pro': 5000,
    'premium': None,
}


def get_effective_plan(user) -> str:
    from accounts.models import UserRole
    from churches.models import Subscription

    if not user.is_authenticated:
        return 'free'
    if getattr(user, 'role', None) == UserRole.SUPER_ADMIN and not getattr(user, 'church_id', None):
        return 'premium'
    ch = getattr(user, 'church', None)
    if not ch:
        return 'free'
    sub = (
        Subscription.objects.filter(church=ch, is_active=True)
        .order_by('-created_at')
        .first()
    )
    if not sub or not sub.is_valid_at(timezone.now().date()):
        return 'free'
    return sub.plan


def assert_can_add_fidele(user) -> None:
    """Lève ValidationError si quota atteint."""
    from rest_framework.exceptions import ValidationError  # pyright: ignore[reportMissingImports]

    plan = get_effective_plan(user)
    cap = PLAN_MAX_FIDELES.get(plan)
    if cap is None:
        return
    if not getattr(user, 'church_id', None):
        return
    n = Fidele.objects.filter(church_id=user.church_id, statut='actif').count()
    if n >= cap:
        raise ValidationError(
            {'detail': f'Quota fidèles atteint pour le plan {plan} ({cap}). Passez à un plan supérieur.'},
            code='subscription_limit',
        )


def feature_allowed(user, feature: str) -> bool:
    """Rapports avancés / exports : Premium et Pro selon feature."""
    plan = get_effective_plan(user)
    if plan == 'premium':
        return True
    if plan == 'pro':
        return feature in ('reports_basic', 'exports', 'dashboard')
    return feature in ('dashboard',)
