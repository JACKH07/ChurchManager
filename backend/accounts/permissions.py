from rest_framework.permissions import BasePermission, IsAuthenticated  # noqa: F401 (re-export IsAuthenticated)  # pyright: ignore[reportMissingImports]
from .models import UserRole


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.SUPER_ADMIN


class IsAdminNational(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_at_least(UserRole.ADMIN_NATIONAL)


class IsAdminRegion(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_at_least(UserRole.ADMIN_REGION)


class IsSuperviseurDistrict(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_at_least(UserRole.SUPERVISEUR_DISTRICT)


class IsChefParoisse(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_at_least(UserRole.CHEF_PAROISSE)


class IsPasteurLocal(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_at_least(UserRole.PASTEUR_LOCAL)


class IsTresorier(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_at_least(UserRole.TRESORIER)


class IsPasteurOrTresorier(BasePermission):
    """Pasteur local ou trésorier (gestion cotisations / fidèles côté local)."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_at_least(UserRole.PASTEUR_LOCAL)
            or request.user.role == UserRole.TRESORIER
        )


class IsReadOnly(BasePermission):
    """Autorise uniquement les méthodes de lecture (GET, HEAD, OPTIONS)."""
    def has_permission(self, request, view):
        return request.method in ('GET', 'HEAD', 'OPTIONS')
