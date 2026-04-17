"""
Attache request.church et refuse les utilisateurs sans église (hors SuperAdmin plateforme).
Vérifie l'abonnement actif pour les routes API métier.
"""

from django.http import JsonResponse # type: ignore from django.http

from accounts.models import UserRole
from common.tenant import user_has_active_subscription


class TenantSubscriptionMiddleware:
    """À placer après AuthenticationMiddleware."""

    EXEMPT_PREFIXES = (
        '/admin/',
        '/api/schema',
        '/api/docs/',
        '/api/redoc/',
        '/static/',
        '/media/',
    )
    EXEMPT_PATHS = frozenset({'/', '/api/v1/auth/login/', '/api/v1/auth/register/', '/api/v1/auth/refresh/'})

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.church = getattr(request.user, 'church', None) if request.user.is_authenticated else None

        path = request.path
        if any(path.startswith(p) for p in self.EXEMPT_PREFIXES) or path in self.EXEMPT_PATHS:
            return self.get_response(request)

        if path.startswith('/api/v1/auth/'):
            return self.get_response(request)

        if path.startswith('/api/') and request.user.is_authenticated:
            u = request.user
            if getattr(u, 'role', None) == UserRole.SUPER_ADMIN and not getattr(u, 'church_id', None):
                return self.get_response(request)
            if not getattr(u, 'church_id', None):
                return JsonResponse(
                    {'detail': 'Aucune organisation associée à ce compte. Contactez l’administrateur.'},
                    status=403,
                )
            if not user_has_active_subscription(u):
                return JsonResponse(
                    {'detail': 'Abonnement inactif ou expiré. Renouvelez votre abonnement pour continuer.', 'code': 'subscription_inactive'},
                    status=402,
                )

        return self.get_response(request)
