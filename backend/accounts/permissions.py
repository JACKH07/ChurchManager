from rest_framework.permissions import BasePermission, IsAuthenticated  # noqa: F401 (re-export IsAuthenticated)
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


class IsReadOnly(BasePermission):
    """Autorise uniquement les méthodes de lecture (GET, HEAD, OPTIONS)."""
    def has_permission(self, request, view):
        return request.method in ('GET', 'HEAD', 'OPTIONS')
