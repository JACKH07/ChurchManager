from django.db import models as db_models # type: ignore from django.db 
from django.utils import timezone # type: ignore from django.utils
from rest_framework import viewsets, filters, status # type: ignore from rest_framework
from rest_framework.decorators import action # type: ignore from rest_framework.decorators
from rest_framework.response import Response # type: ignore from rest_framework.response
from django_filters.rest_framework import DjangoFilterBackend # type: ignore from django_filters.rest_framework
from drf_spectacular.utils import extend_schema # type: ignore from drf_spectacular.utils

from .models import Cotisation, Recu, ObjectifCotisation
from .serializers import (
    CotisationSerializer, CotisationListSerializer,
    RecuSerializer, ObjectifCotisationSerializer,
)
from accounts.permissions import IsAuthenticated, IsPasteurLocal, IsChefParoisse
from accounts.mixins import ScopedQuerysetMixin


@extend_schema(tags=['contributions'])
class CotisationViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = Cotisation.objects.select_related('fidele', 'enregistre_par', 'valide_par').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'type_cotisation', 'statut', 'mode_paiement',
        'fidele', 'periode_mois', 'periode_annee',
        'niveau_entite',
    ]
    search_fields = ['reference', 'fidele__nom', 'fidele__prenom', 'fidele__code_fidele']
    ordering_fields = ['date_paiement', 'montant', 'created_at']
    permission_classes = [IsAuthenticated]

    scope_region_filter = 'fidele__eglise__paroisse__district__region_id'
    scope_district_filter = 'fidele__eglise__paroisse__district_id'
    scope_paroisse_filter = 'fidele__eglise__paroisse_id'
    scope_eglise_filter = 'fidele__eglise_id'

    def get_queryset(self):
        return self.get_scoped_queryset(super().get_queryset())

    def get_serializer_class(self):
        if self.action == 'list':
            return CotisationListSerializer
        return CotisationSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            return [IsPasteurLocal()]
        if self.action == 'destroy':
            return [IsChefParoisse()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['post'], permission_classes=[IsChefParoisse])
    def valider(self, request, pk=None):
        cotisation = self.get_object()
        if cotisation.statut != 'en_attente':
            return Response({'detail': 'Seules les cotisations en attente peuvent être validées.'}, status=400)
        cotisation.statut = 'valide'
        cotisation.valide_par = request.user
        cotisation.date_validation = timezone.now()
        cotisation.save()
        # Générer le reçu
        self._generer_recu(cotisation, request.user)
        return Response(CotisationSerializer(cotisation, context={'request': request}).data)

    @action(detail=True, methods=['post'], permission_classes=[IsChefParoisse])
    def rejeter(self, request, pk=None):
        cotisation = self.get_object()
        cotisation.statut = 'rejete'
        cotisation.notes = request.data.get('motif', cotisation.notes)
        cotisation.save()
        return Response(CotisationSerializer(cotisation, context={'request': request}).data)

    def _generer_recu(self, cotisation, user):
        import random
        numero = f"REC-{timezone.now().year}{timezone.now().month:02d}-{''.join([str(random.randint(0,9)) for _ in range(6)])}"
        Recu.objects.get_or_create(
            cotisation=cotisation,
            defaults={'numero_recu': numero, 'genere_par': user}
        )

    @action(detail=False, methods=['get'])
    def resume(self, request):
        """Résumé financier selon les filtres"""
        qs = self.filter_queryset(self.get_queryset()).filter(statut='valide')
        total = qs.aggregate(total=db_models.Sum('montant'))['total'] or 0
        par_type = {}
        for item in qs.values('type_cotisation').annotate(total=db_models.Sum('montant')):
            par_type[item['type_cotisation']] = float(item['total'])
        par_mode = {}
        for item in qs.values('mode_paiement').annotate(total=db_models.Sum('montant')):
            par_mode[item['mode_paiement']] = float(item['total'])

        return Response({
            'total_collecte': float(total),
            'nombre_cotisations': qs.count(),
            'par_type': par_type,
            'par_mode_paiement': par_mode,
        })

    @action(detail=False, methods=['get'])
    def evolution_mensuelle(self, request):
        """Évolution des cotisations mois par mois pour l'année courante"""
        annee = int(request.query_params.get('annee', timezone.now().year))
        qs = self.filter_queryset(self.get_queryset()).filter(
            statut='valide', periode_annee=annee
        )
        result = []
        MOIS = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        for mois in range(1, 13):
            montant = qs.filter(periode_mois=mois).aggregate(
                total=db_models.Sum('montant')
            )['total'] or 0
            result.append({'mois': MOIS[mois - 1], 'montant': float(montant)})
        return Response(result)

    @action(detail=False, methods=['get'])
    def impayés(self, request):
        """Liste des fidèles n'ayant pas payé pour une période donnée"""
        mois = int(request.query_params.get('mois', timezone.now().month))
        annee = int(request.query_params.get('annee', timezone.now().year))
        eglise_id = request.query_params.get('eglise')

        from members.models import Fidele
        fideles_qs = Fidele.objects.filter(statut='actif')
        if eglise_id:
            fideles_qs = fideles_qs.filter(eglise_id=eglise_id)

        fideles_ayant_paye = Cotisation.objects.filter(
            type_cotisation='mensuelle_membre',
            periode_mois=mois,
            periode_annee=annee,
            statut='valide',
        ).values_list('fidele_id', flat=True)

        impayés = fideles_qs.exclude(id__in=fideles_ayant_paye)
        from members.serializers import FideleListSerializer
        serializer = FideleListSerializer(impayés, many=True)
        return Response({'total': impayés.count(), 'fideles': serializer.data})


@extend_schema(tags=['contributions'])
class RecuViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Recu.objects.select_related('cotisation', 'genere_par').all()
    serializer_class = RecuSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['cotisation__fidele', 'genere_par']
    permission_classes = [IsAuthenticated]


@extend_schema(tags=['contributions'])
class ObjectifCotisationViewSet(viewsets.ModelViewSet):
    queryset = ObjectifCotisation.objects.all()
    serializer_class = ObjectifCotisationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['niveau_entite', 'entite_id', 'type_cotisation', 'periode_annee']
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsChefParoisse()]
        return [IsAuthenticated()]
