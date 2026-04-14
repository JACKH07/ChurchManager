from django.contrib import admin # type: ignore
from .models import Evenement, InscriptionEvenement, Annonce


@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ['titre', 'type_evenement', 'date_debut', 'lieu', 'niveau_visibilite', 'inscription_requise']
    list_filter = ['type_evenement', 'niveau_visibilite', 'est_public']
    search_fields = ['titre', 'lieu']


@admin.register(InscriptionEvenement)
class InscriptionEvenementAdmin(admin.ModelAdmin):
    list_display = ['evenement', 'fidele', 'statut', 'date_inscription']
    list_filter = ['statut']


@admin.register(Annonce)
class AnnonceAdmin(admin.ModelAdmin):
    list_display = ['titre', 'niveau_visibilite', 'est_epingle', 'date_expiration', 'auteur']
    list_filter = ['niveau_visibilite', 'est_epingle']
    search_fields = ['titre', 'contenu']
