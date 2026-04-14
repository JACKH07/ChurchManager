from rest_framework import viewsets, filters # type: ignore from rest_framework 
from rest_framework.decorators import action # type: ignore from rest_framework.decorators
from rest_framework.response import Response # type: ignore from rest_framework.response
from django_filters.rest_framework import DjangoFilterBackend # type: ignore from django_filters.rest_framework
from drf_spectacular.utils import extend_schema, extend_schema_view # type: ignore from drf_spectacular.utils

from .models import National, Region, District, Paroisse, EgliseLocale
from .serializers import (
    NationalSerializer, RegionSerializer, DistrictSerializer,
    ParoisseSerializer, EgliseLocaleSerializer, HierarchieCompleteSerializer,
)
from accounts.permissions import IsAdminNational, IsAdminRegion, IsAuthenticated


@extend_schema(tags=['hierarchy'])
class NationalViewSet(viewsets.ModelViewSet):
    queryset = National.objects.all()
    serializer_class = NationalSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminNational()]
        return [IsAuthenticated()]


@extend_schema(tags=['hierarchy'])
@extend_schema_view(
    list=extend_schema(summary='Liste des régions'),
    create=extend_schema(summary='Créer une région'),
)
class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.select_related('national', 'responsable').all()
    serializer_class = RegionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['national']
    search_fields = ['nom', 'code']
    ordering_fields = ['nom', 'code', 'created_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminNational()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['get'])
    def hierarchie(self, request, pk=None):
        region = self.get_object()
        serializer = HierarchieCompleteSerializer(region)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def statistiques(self, request, pk=None):
        region = self.get_object()
        total_districts = region.districts.count()
        total_paroisses = sum(d.paroisses.count() for d in region.districts.all())
        total_eglises = sum(
            p.eglises.count()
            for d in region.districts.all()
            for p in d.paroisses.all()
        )
        total_fideles = sum(
            e.fideles.filter(statut='actif').count()
            for d in region.districts.all()
            for p in d.paroisses.all()
            for e in p.eglises.all()
        )
        return Response({
            'region': region.nom,
            'total_districts': total_districts,
            'total_paroisses': total_paroisses,
            'total_eglises': total_eglises,
            'total_fideles': total_fideles,
        })


@extend_schema(tags=['hierarchy'])
class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.select_related('region', 'superviseur').all()
    serializer_class = DistrictSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['region']
    search_fields = ['nom', 'code']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminRegion()]
        return [IsAuthenticated()]


@extend_schema(tags=['hierarchy'])
class ParoisseViewSet(viewsets.ModelViewSet):
    queryset = Paroisse.objects.select_related('district__region', 'chef').all()
    serializer_class = ParoisseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['district', 'district__region']
    search_fields = ['nom', 'code']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            from accounts.permissions import IsSuperviseurDistrict
            return [IsSuperviseurDistrict()]
        return [IsAuthenticated()]


@extend_schema(tags=['hierarchy'])
class EgliseLocaleViewSet(viewsets.ModelViewSet):
    queryset = EgliseLocale.objects.select_related('paroisse__district__region', 'pasteur').all()
    serializer_class = EgliseLocaleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['paroisse', 'paroisse__district', 'paroisse__district__region']
    search_fields = ['nom', 'code']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            from accounts.permissions import IsChefParoisse
            return [IsChefParoisse()]
        return [IsAuthenticated()]
