from rest_framework import serializers # type: ignore from rest_framework
from .models import National, Region, District, Paroisse, EgliseLocale


class NationalSerializer(serializers.ModelSerializer):
    total_regions = serializers.SerializerMethodField()

    class Meta:
        model = National
        fields = '__all__'

    def get_total_regions(self, obj):
        return obj.regions.count()


class RegionSerializer(serializers.ModelSerializer):
    national_nom = serializers.CharField(source='national.nom', read_only=True)
    responsable_nom = serializers.CharField(source='responsable.full_name', read_only=True)
    total_districts = serializers.SerializerMethodField()
    national = serializers.PrimaryKeyRelatedField(
        queryset=National.objects.all(), required=False
    )

    class Meta:
        model = Region
        fields = '__all__'

    def get_total_districts(self, obj):
        return obj.districts.count()

    def validate(self, attrs):
        # Si national n'est pas fourni, utiliser le premier (ou créer un par défaut)
        if 'national' not in attrs or attrs.get('national') is None:
            national = National.objects.first()
            if national is None:
                raise serializers.ValidationError(
                    {'national': "Aucune organisation nationale n'existe. Créez-en une d'abord dans l'administration."}
                )
            attrs['national'] = national
        return attrs


class DistrictSerializer(serializers.ModelSerializer):
    region_nom = serializers.CharField(source='region.nom', read_only=True)
    region_code = serializers.CharField(source='region.code', read_only=True)
    superviseur_nom = serializers.CharField(source='superviseur.full_name', read_only=True)
    code_complet = serializers.ReadOnlyField()
    total_paroisses = serializers.SerializerMethodField()

    class Meta:
        model = District
        fields = '__all__'

    def get_total_paroisses(self, obj):
        return obj.paroisses.count()


class ParoisseSerializer(serializers.ModelSerializer):
    district_nom = serializers.CharField(source='district.nom', read_only=True)
    chef_nom = serializers.CharField(source='chef.full_name', read_only=True)
    total_eglises = serializers.SerializerMethodField()

    class Meta:
        model = Paroisse
        fields = '__all__'

    def get_total_eglises(self, obj):
        return obj.eglises.count()


class EgliseLocaleSerializer(serializers.ModelSerializer):
    paroisse_nom = serializers.CharField(source='paroisse.nom', read_only=True)
    pasteur_nom = serializers.CharField(source='pasteur.full_name', read_only=True)
    code_complet = serializers.ReadOnlyField()
    total_fideles = serializers.SerializerMethodField()

    class Meta:
        model = EgliseLocale
        fields = '__all__'

    def get_total_fideles(self, obj):
        return obj.fideles.filter(statut='actif').count()


class HierarchieCompleteSerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'arbre hiérarchique complet"""
    districts = serializers.SerializerMethodField()
    total_fideles = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ['id', 'code', 'nom', 'districts', 'total_fideles']

    def get_districts(self, obj):
        districts = obj.districts.prefetch_related('paroisses__eglises')
        result = []
        for d in districts:
            paroisses = []
            for p in d.paroisses.all():
                eglises = [{'id': e.id, 'nom': e.nom, 'code': e.code} for e in p.eglises.all()]
                paroisses.append({'id': p.id, 'nom': p.nom, 'code': p.code, 'eglises': eglises})
            result.append({'id': d.id, 'nom': d.nom, 'code': d.code, 'paroisses': paroisses})
        return result

    def get_total_fideles(self, obj):
        return sum(
            e.fideles.filter(statut='actif').count()
            for d in obj.districts.all()
            for p in d.paroisses.all()
            for e in p.eglises.all()
        )
