from django.contrib import admin # type: ignore
from .models import Fidele, Ministere, TransfertFidele


@admin.register(Fidele)
class FideleAdmin(admin.ModelAdmin):
    list_display = ['code_fidele', 'nom', 'prenom', 'genre', 'eglise', 'statut', 'date_inscription']
    list_filter = ['statut', 'genre', 'situation_familiale', 'eglise__paroisse__district__region']
    search_fields = ['nom', 'prenom', 'code_fidele', 'telephone', 'email']
    readonly_fields = ['code_fidele', 'created_at', 'updated_at']
    filter_horizontal = ['ministeres']
    fieldsets = (
        ('Identité', {'fields': ('code_fidele', 'nom', 'prenom', 'genre', 'date_naissance', 'lieu_naissance', 'photo')}),
        ('Situation', {'fields': ('situation_familiale', 'nombre_enfants', 'profession')}),
        ('Contacts', {'fields': ('telephone', 'telephone_2', 'email', 'adresse')}),
        ('Ecclésiastic', {'fields': ('eglise', 'ministeres', 'statut', 'date_inscription', 'date_bapteme')}),
        ('Compte', {'fields': ('user', 'notes')}),
        ('Métadonnées', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Ministere)
class MinistereAdmin(admin.ModelAdmin):
    list_display = ['nom', 'eglise']
    list_filter = ['eglise__paroisse__district__region']
    search_fields = ['nom']


@admin.register(TransfertFidele)
class TransfertFideleAdmin(admin.ModelAdmin):
    list_display = ['fidele', 'eglise_origine', 'eglise_destination', 'date_transfert', 'approuve_par']
    list_filter = ['date_transfert']
    search_fields = ['fidele__nom', 'fidele__prenom', 'fidele__code_fidele']
