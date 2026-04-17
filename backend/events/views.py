from rest_framework import viewsets, filters, status # type: ignore from rest_framework
from rest_framework.decorators import action # type: ignore from rest_framework.decorators
from rest_framework.response import Response # type: ignore from rest_framework.response
from django_filters.rest_framework import DjangoFilterBackend # type: ignore from django_filters.rest_framework
from drf_spectacular.utils import extend_schema # type: ignore from drf_spectacular.utils

from common.viewsets import TenantScopedModelViewSet

from .models import Evenement, InscriptionEvenement, Annonce
from .serializers import EvenementSerializer, InscriptionEvenementSerializer, AnnonceSerializer
from accounts.models import UserRole
from accounts.permissions import IsAuthenticated, IsPasteurLocal


@extend_schema(tags=['events'])
class EvenementViewSet(TenantScopedModelViewSet):
    queryset = Evenement.objects.select_related('createur', 'church').all()
    serializer_class = EvenementSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['niveau_visibilite', 'type_evenement', 'est_public', 'inscription_requise']
    search_fields = ['titre', 'description', 'lieu']
    ordering_fields = ['date_debut', 'created_at']
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsPasteurLocal()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['post'])
    def inscrire(self, request, pk=None):
        evenement = self.get_object()
        fidele_id = request.data.get('fidele')

        if not fidele_id:
            return Response({'detail': 'Le champ fidele est requis.'}, status=400)

        from members.models import Fidele
        try:
            fidele = Fidele.objects.get(pk=fidele_id)
        except Fidele.DoesNotExist:
            return Response({'detail': 'Fidèle introuvable.'}, status=404)

        user = request.user
        if request.user.church_id and fidele.church_id != request.user.church_id:
            return Response({'detail': 'Fidèle hors de votre organisation.'}, status=403)
        if not user.is_at_least(UserRole.ADMIN_NATIONAL):
            if user.entity_id and fidele.eglise_id != user.entity_id:
                if not user.is_at_least(UserRole.CHEF_PAROISSE):
                    return Response(
                        {'detail': 'Vous ne pouvez pas inscrire un fidèle hors de votre périmètre.'},
                        status=403
                    )

        if evenement.places_disponibles is not None and evenement.places_disponibles <= 0:
            return Response({'detail': 'Plus de places disponibles.'}, status=400)

        statut_inscription = 'en_attente' if evenement.inscription_requise else 'confirme'
        inscription, created = InscriptionEvenement.objects.get_or_create(
            evenement=evenement,
            fidele=fidele,
            defaults={'statut': statut_inscription, 'church': evenement.church},
        )
        if not created:
            return Response({'detail': 'Ce fidèle est déjà inscrit à cet événement.'}, status=400)
        return Response(InscriptionEvenementSerializer(inscription).data, status=201)

    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        evenement = self.get_object()
        inscriptions = evenement.inscriptions.select_related('fidele').all()
        serializer = InscriptionEvenementSerializer(inscriptions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def a_venir(self, request):
        from django.utils import timezone # type: ignore from django.utils
        qs = self.filter_queryset(self.get_queryset()).filter(date_debut__gte=timezone.now())
        serializer = self.get_serializer(qs[:10], many=True)
        return Response(serializer.data)


@extend_schema(tags=['events'])
class AnnonceViewSet(TenantScopedModelViewSet):
    queryset = Annonce.objects.select_related('auteur', 'church').all()
    serializer_class = AnnonceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['niveau_visibilite', 'est_epingle', 'entite_id']
    search_fields = ['titre', 'contenu']
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsPasteurLocal()]
        return [IsAuthenticated()]
