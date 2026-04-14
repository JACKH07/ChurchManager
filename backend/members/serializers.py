from rest_framework import serializers # type: ignore from rest_framework
from .models import Fidele, Ministere, TransfertFidele


class MinistereSerializer(serializers.ModelSerializer):
    total_membres = serializers.SerializerMethodField()

    class Meta:
        model = Ministere
        fields = '__all__'

    def get_total_membres(self, obj):
        return obj.membres.filter(statut='actif').count()


class FideleSerializer(serializers.ModelSerializer):
    nom_complet = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    eglise_nom = serializers.CharField(source='eglise.nom', read_only=True)
    eglise_code = serializers.CharField(source='eglise.code_complet', read_only=True)
    ministeres_noms = serializers.SerializerMethodField()

    class Meta:
        model = Fidele
        fields = '__all__'
        read_only_fields = ['code_fidele', 'created_at', 'updated_at']

    def get_ministeres_noms(self, obj):
        return [m.nom for m in obj.ministeres.all()]


class FideleListSerializer(serializers.ModelSerializer):
    """Sérialiseur allégé pour les listes"""
    nom_complet = serializers.ReadOnlyField()
    eglise_nom = serializers.CharField(source='eglise.nom', read_only=True)

    class Meta:
        model = Fidele
        fields = ['id', 'code_fidele', 'nom', 'prenom', 'nom_complet', 'genre',
                  'telephone', 'email', 'statut', 'eglise', 'eglise_nom',
                  'date_inscription', 'photo']


class TransfertFideleSerializer(serializers.ModelSerializer):
    fidele_nom = serializers.CharField(source='fidele.nom_complet', read_only=True)
    eglise_origine_nom = serializers.CharField(source='eglise_origine.nom', read_only=True)
    eglise_destination_nom = serializers.CharField(source='eglise_destination.nom', read_only=True)

    class Meta:
        model = TransfertFidele
        fields = '__all__'
        read_only_fields = ['approuve_par', 'created_at']
