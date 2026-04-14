from django.contrib import admin # type: ignore
from .models import Cotisation, Recu, ObjectifCotisation


@admin.register(Cotisation)
class CotisationAdmin(admin.ModelAdmin):
    list_display = ['reference', 'fidele', 'type_cotisation', 'montant', 'devise', 'mode_paiement', 'statut', 'date_paiement']
    list_filter = ['type_cotisation', 'statut', 'mode_paiement', 'periode_annee', 'periode_mois']
    search_fields = ['reference', 'fidele__nom', 'fidele__prenom', 'fidele__code_fidele']
    readonly_fields = ['reference', 'created_at', 'updated_at']


@admin.register(Recu)
class RecuAdmin(admin.ModelAdmin):
    list_display = ['numero_recu', 'cotisation', 'genere_le', 'genere_par']
    readonly_fields = ['numero_recu', 'genere_le']


@admin.register(ObjectifCotisation)
class ObjectifCotisationAdmin(admin.ModelAdmin):
    list_display = ['niveau_entite', 'entite_id', 'type_cotisation', 'montant_objectif', 'periode_mois', 'periode_annee']
    list_filter = ['niveau_entite', 'type_cotisation', 'periode_annee']
