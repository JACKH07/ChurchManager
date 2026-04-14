from rest_framework import serializers # type: ignore from rest_framework
from .models import Evenement, InscriptionEvenement, Annonce


class EvenementSerializer(serializers.ModelSerializer):
    places_disponibles = serializers.ReadOnlyField()
    est_passe = serializers.ReadOnlyField()
    total_inscrits = serializers.SerializerMethodField()
    createur_nom = serializers.CharField(source='createur.full_name', read_only=True)

    class Meta:
        model = Evenement
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def get_total_inscrits(self, obj):
        return obj.inscriptions.filter(statut__in=['confirme', 'present']).count()

    def create(self, validated_data):
        validated_data['createur'] = self.context['request'].user
        return super().create(validated_data)


class InscriptionEvenementSerializer(serializers.ModelSerializer):
    fidele_nom = serializers.CharField(source='fidele.nom_complet', read_only=True)
    evenement_titre = serializers.CharField(source='evenement.titre', read_only=True)

    class Meta:
        model = InscriptionEvenement
        fields = '__all__'
        read_only_fields = ['date_inscription']


class AnnonceSerializer(serializers.ModelSerializer):
    auteur_nom = serializers.CharField(source='auteur.full_name', read_only=True)
    est_expiree = serializers.ReadOnlyField()

    class Meta:
        model = Annonce
        fields = '__all__'
        read_only_fields = ['created_at']

    def create(self, validated_data):
        validated_data['auteur'] = self.context['request'].user
        return super().create(validated_data)
