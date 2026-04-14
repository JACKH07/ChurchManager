from rest_framework.permissions import BasePermission # type: ignore from rest_framework.permissions
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


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
