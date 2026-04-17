from rest_framework import serializers # type: ignore from rest_framework
from django.utils import timezone # type: ignore from django.utils
from django.db.models import Sum # type: ignore from django.db.models   
from .models import Cotisation, Recu, ObjectifCotisation # type: ignore from local app  


class CotisationSerializer(serializers.ModelSerializer):
    fidele_nom = serializers.CharField(source='fidele.nom_complet', read_only=True)
    fidele_code = serializers.CharField(source='fidele.code_fidele', read_only=True)
    type_cotisation_display = serializers.CharField(source='get_type_cotisation_display', read_only=True)
    mode_paiement_display = serializers.CharField(source='get_mode_paiement_display', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    enregistre_par_nom = serializers.CharField(source='enregistre_par.full_name', read_only=True)

    class Meta:
        model = Cotisation
        fields = '__all__'
        read_only_fields = ['reference', 'created_at', 'updated_at', 'valide_par', 'date_validation']

    def create(self, validated_data):
        validated_data['enregistre_par'] = self.context['request'].user
        return super().create(validated_data)


class CotisationListSerializer(serializers.ModelSerializer):
    fidele_nom = serializers.CharField(source='fidele.nom_complet', read_only=True)
    type_cotisation_display = serializers.CharField(source='get_type_cotisation_display', read_only=True)

    class Meta:
        model = Cotisation
        fields = ['id', 'reference', 'fidele', 'fidele_nom', 'type_cotisation',
                  'type_cotisation_display', 'montant', 'devise', 'mode_paiement',
                  'statut', 'periode_mois', 'periode_annee', 'date_paiement']


class RecuSerializer(serializers.ModelSerializer):
    cotisation_reference = serializers.CharField(source='cotisation.reference', read_only=True)

    class Meta:
        model = Recu
        fields = '__all__'
        read_only_fields = ['numero_recu', 'genere_le', 'genere_par']


class ObjectifCotisationSerializer(serializers.ModelSerializer):
    taux_realisation = serializers.SerializerMethodField()

    class Meta:
        model = ObjectifCotisation
        fields = '__all__'

    def get_taux_realisation(self, obj):
        qs = Cotisation.objects.filter(
            niveau_entite=obj.niveau_entite,
            entite_id=obj.entite_id,
            type_cotisation=obj.type_cotisation,
            periode_mois=obj.periode_mois,
            periode_annee=obj.periode_annee,
            statut='valide',
        )
        if obj.church_id:
            qs = qs.filter(church_id=obj.church_id)
        total = qs.aggregate(total=Sum('montant'))['total'] or 0
        if obj.montant_objectif > 0:
            return round(float(total) / float(obj.montant_objectif) * 100, 2)
        return 0


class SommaireFinancierSerializer(serializers.Serializer):
    periode = serializers.CharField()
    total_collecte = serializers.DecimalField(max_digits=12, decimal_places=2)
    nombre_cotisations = serializers.IntegerField()
    par_type = serializers.DictField()
    par_mode_paiement = serializers.DictField()
    evolution = serializers.ListField()
