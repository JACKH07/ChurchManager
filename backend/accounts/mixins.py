"""
Mixin de filtrage par périmètre selon le rôle de l'utilisateur.
Le filtre multi-tenant (church) est appliqué en premier.
"""
from common.tenant import filter_queryset_for_tenant

from .models import UserRole


class ScopedQuerysetMixin:
    """
    Restreint automatiquement le queryset selon le rôle et l'entité de l'utilisateur.
    Le viewset doit définir :
      - scope_region_filter     : str   → champ FK region (ex: 'eglise__paroisse__district__region_id')
      - scope_district_filter   : str   → champ FK district
      - scope_paroisse_filter   : str   → champ FK paroisse
      - scope_eglise_filter     : str   → champ FK eglise
    """
    scope_region_filter: str = ''
    scope_district_filter: str = ''
    scope_paroisse_filter: str = ''
    scope_eglise_filter: str = ''

    def get_scoped_queryset(self, queryset):
        user = self.request.user  # type: ignore[attr-defined]

        if not user.is_authenticated:
            return queryset.none()

        qs = filter_queryset_for_tenant(queryset, user)

        if user.is_at_least(UserRole.ADMIN_NATIONAL):
            return qs

        entity_id = user.entity_id
        if not entity_id:
            return qs.none()

        if user.role == UserRole.ADMIN_REGION and self.scope_region_filter:
            return qs.filter(**{self.scope_region_filter: entity_id})

        if user.role == UserRole.SUPERVISEUR_DISTRICT and self.scope_district_filter:
            return qs.filter(**{self.scope_district_filter: entity_id})

        if user.role == UserRole.CHEF_PAROISSE and self.scope_paroisse_filter:
            return qs.filter(**{self.scope_paroisse_filter: entity_id})

        if user.role in (UserRole.PASTEUR_LOCAL, UserRole.TRESORIER, UserRole.FIDELE) and self.scope_eglise_filter:
            return qs.filter(**{self.scope_eglise_filter: entity_id})

        return qs.none()
