import io
import qrcode  # pyright: ignore[reportMissingModuleSource]
from django.http import HttpResponse  # pyright: ignore[reportMissingImports]
from reportlab.lib.pagesizes import A4  # pyright: ignore[reportMissingModuleSource]
from reportlab.lib import colors  # pyright: ignore[reportMissingModuleSource]
from reportlab.lib.units import mm  # pyright: ignore[reportMissingModuleSource]
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image  # pyright: ignore[reportMissingModuleSource]
from reportlab.lib.styles import getSampleStyleSheet  # pyright: ignore[reportMissingModuleSource]
from rest_framework import viewsets, filters, status  # pyright: ignore[reportMissingImports]
from rest_framework.decorators import action  # pyright: ignore[reportMissingImports]
from rest_framework.response import Response  # pyright: ignore[reportMissingImports]
from django_filters.rest_framework import DjangoFilterBackend  # pyright: ignore[reportMissingImports]
from drf_spectacular.utils import extend_schema  # pyright: ignore[reportMissingImports]

from .models import Fidele, Ministere, TransfertFidele
from .serializers import FideleSerializer, FideleListSerializer, MinistereSerializer, TransfertFideleSerializer
from accounts.permissions import IsAuthenticated, IsChefParoisse, IsPasteurLocal
from accounts.mixins import ScopedQuerysetMixin


@extend_schema(tags=['members'])
class FideleViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = Fidele.objects.select_related('eglise__paroisse__district__region').prefetch_related('ministeres').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['statut', 'genre', 'eglise', 'eglise__paroisse', 'eglise__paroisse__district',
                        'eglise__paroisse__district__region', 'situation_familiale']
    search_fields = ['nom', 'prenom', 'code_fidele', 'telephone', 'email']
    ordering_fields = ['nom', 'prenom', 'date_inscription', 'created_at']
    permission_classes = [IsAuthenticated]

    scope_region_filter = 'eglise__paroisse__district__region_id'
    scope_district_filter = 'eglise__paroisse__district_id'
    scope_paroisse_filter = 'eglise__paroisse_id'
    scope_eglise_filter = 'eglise_id'

    def get_queryset(self):
        return self.get_scoped_queryset(super().get_queryset())

    def get_serializer_class(self):
        if self.action == 'list':
            return FideleListSerializer
        return FideleSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsPasteurLocal()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['get'])
    def carte_membre(self, request, pk=None):
        """Génère la carte de membre en PDF avec QR code"""
        fidele = self.get_object()
        buffer = io.BytesIO()

        # Dimensions carte de membre (85.6mm x 54mm)
        from reportlab.lib.pagesizes import landscape  # pyright: ignore[reportMissingModuleSource]
        from reportlab.lib.units import mm  # pyright: ignore[reportMissingModuleSource]
        page_width = 85.6 * mm
        page_height = 54 * mm

        doc = SimpleDocTemplate(buffer, pagesize=(page_width, page_height),
                                leftMargin=3*mm, rightMargin=3*mm,
                                topMargin=3*mm, bottomMargin=3*mm)

        # Générer QR Code
        qr = qrcode.QRCode(version=1, box_size=4, border=1)
        qr.add_data(fidele.code_fidele)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)

        styles = getSampleStyleSheet()
        elements = []

        title_style = styles['Title']
        title_style.fontSize = 8
        title_style.leading = 10

        normal_style = styles['Normal']
        normal_style.fontSize = 6
        normal_style.leading = 8

        elements.append(Paragraph("CARTE DE MEMBRE", title_style))
        elements.append(Paragraph(f"<b>{fidele.nom_complet.upper()}</b>", normal_style))
        elements.append(Paragraph(f"Code: {fidele.code_fidele}", normal_style))
        elements.append(Paragraph(f"Église: {fidele.eglise.nom}", normal_style))
        elements.append(Paragraph(f"Statut: {fidele.get_statut_display()}", normal_style))

        # QR Code
        qr_image = Image(qr_buffer, width=20*mm, height=20*mm)
        elements.append(qr_image)

        doc.build(elements)
        buffer.seek(0)

        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="carte_membre_{fidele.code_fidele}.pdf"'
        return response

    @action(detail=True, methods=['get'])
    def qrcode(self, request, pk=None):
        """Retourne le QR code du fidèle en PNG"""
        fidele = self.get_object()
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(fidele.code_fidele)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return HttpResponse(buffer.read(), content_type='image/png')

    @action(detail=True, methods=['post'], permission_classes=[IsChefParoisse])
    def transferer(self, request, pk=None):
        """Transférer un fidèle vers une autre église"""
        fidele = self.get_object()
        serializer = TransfertFideleSerializer(data={
            **request.data,
            'fidele': fidele.id,
            'eglise_origine': fidele.eglise.id,
        })
        serializer.is_valid(raise_exception=True)
        transfert = serializer.save(approuve_par=request.user)
        # Le fidèle reste actif dans sa nouvelle église
        fidele.eglise = transfert.eglise_destination
        fidele.statut = 'actif'
        fidele.save()
        return Response(TransfertFideleSerializer(transfert).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'actifs': qs.filter(statut='actif').count(),
            'inactifs': qs.filter(statut='inactif').count(),
            'transferes': qs.filter(statut='transfere').count(),
            'decedes': qs.filter(statut='decede').count(),
            'hommes': qs.filter(genre='H').count(),
            'femmes': qs.filter(genre='F').count(),
        })


@extend_schema(tags=['members'])
class MinistereViewSet(viewsets.ModelViewSet):
    queryset = Ministere.objects.select_related('eglise').all()
    serializer_class = MinistereSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['eglise']
    search_fields = ['nom']
    permission_classes = [IsAuthenticated]


@extend_schema(tags=['members'])
class TransfertFideleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TransfertFidele.objects.select_related('fidele', 'eglise_origine', 'eglise_destination').all()
    serializer_class = TransfertFideleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['fidele', 'eglise_origine', 'eglise_destination']
    permission_classes = [IsAuthenticated]
