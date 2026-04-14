import io
from django.db import models as db_models  # pyright: ignore[reportMissingImports]
from django.utils import timezone  # pyright: ignore[reportMissingImports]
from rest_framework.views import APIView  # pyright: ignore[reportMissingImports]
from rest_framework.response import Response  # pyright: ignore[reportMissingImports]
from rest_framework.decorators import api_view, permission_classes  # pyright: ignore[reportMissingImports]
from drf_spectacular.utils import extend_schema  # pyright: ignore[reportMissingImports]

from accounts.permissions import IsAuthenticated, IsAdminRegion, IsChefParoisse
from members.models import Fidele
from contributions.models import Cotisation
from hierarchy.models import Region, District, Paroisse, EgliseLocale
from events.models import Evenement


@extend_schema(tags=['dashboard'])
class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()
        mois_courant = now.month
        annee_courante = now.year

        # Statistiques globales
        stats = {
            'total_fideles': Fidele.objects.filter(statut='actif').count(),
            'total_regions': Region.objects.count(),
            'total_districts': District.objects.count(),
            'total_paroisses': Paroisse.objects.count(),
            'total_eglises': EgliseLocale.objects.count(),
            'nouveaux_fideles_mois': Fidele.objects.filter(
                date_inscription__month=mois_courant,
                date_inscription__year=annee_courante,
            ).count(),
        }

        # Finances du mois
        cotisations_mois = Cotisation.objects.filter(
            statut='valide',
            periode_mois=mois_courant,
            periode_annee=annee_courante,
        )
        stats['recettes_mois'] = float(
            cotisations_mois.aggregate(total=db_models.Sum('montant'))['total'] or 0
        )
        stats['nombre_paiements_mois'] = cotisations_mois.count()

        # Évolution 6 derniers mois
        MOIS = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        evolution = []
        for i in range(5, -1, -1):
            m = (mois_courant - i - 1) % 12 + 1
            a = annee_courante if mois_courant - i > 0 else annee_courante - 1
            montant = Cotisation.objects.filter(
                statut='valide', periode_mois=m, periode_annee=a
            ).aggregate(total=db_models.Sum('montant'))['total'] or 0
            evolution.append({'mois': MOIS[m - 1], 'montant': float(montant), 'annee': a})
        stats['evolution_cotisations'] = evolution

        # Répartition fidèles par région
        repartition_regions = []
        for region in Region.objects.all():
            total = Fidele.objects.filter(
                eglise__paroisse__district__region=region, statut='actif'
            ).count()
            repartition_regions.append({'region': region.nom, 'code': region.code, 'total': total})
        stats['repartition_regions'] = repartition_regions

        # Taux de cotisation ce mois
        total_fideles_actifs = Fidele.objects.filter(statut='actif').count()
        fideles_ayant_paye = Cotisation.objects.filter(
            type_cotisation='mensuelle_membre',
            statut='valide',
            periode_mois=mois_courant,
            periode_annee=annee_courante,
        ).values('fidele').distinct().count()
        stats['taux_cotisation_mois'] = round(
            (fideles_ayant_paye / total_fideles_actifs * 100) if total_fideles_actifs > 0 else 0, 1
        )

        # Événements à venir
        stats['evenements_a_venir'] = Evenement.objects.filter(
            date_debut__gte=now
        ).count()

        # Alertes
        alertes = []
        if stats['taux_cotisation_mois'] < 50:
            alertes.append({
                'type': 'alerte',
                'message': f"Taux de cotisation bas ce mois : {stats['taux_cotisation_mois']}%"
            })
        stats['alertes'] = alertes

        return Response(stats)


@extend_schema(tags=['reports'])
class RapportFidelesView(APIView):
    permission_classes = [IsChefParoisse]

    def get(self, request):
        eglise_id = request.query_params.get('eglise')
        statut = request.query_params.get('statut', 'actif')
        qs = Fidele.objects.filter(statut=statut)
        if eglise_id:
            qs = qs.filter(eglise_id=eglise_id)

        from members.serializers import FideleSerializer
        return Response({
            'total': qs.count(),
            'fideles': FideleSerializer(qs.select_related('eglise'), many=True).data,
        })


@extend_schema(tags=['reports'])
class RapportFinancierView(APIView):
    permission_classes = [IsChefParoisse]

    def get(self, request):
        mois = int(request.query_params.get('mois', timezone.now().month))
        annee = int(request.query_params.get('annee', timezone.now().year))
        eglise_id = request.query_params.get('eglise')

        qs = Cotisation.objects.filter(statut='valide', periode_mois=mois, periode_annee=annee)
        if eglise_id:
            qs = qs.filter(fidele__eglise_id=eglise_id)

        total = qs.aggregate(total=db_models.Sum('montant'))['total'] or 0
        par_type = {}
        for item in qs.values('type_cotisation').annotate(total=db_models.Sum('montant')):
            par_type[item['type_cotisation']] = float(item['total'])

        return Response({
            'periode': f"{mois:02d}/{annee}",
            'total_collecte': float(total),
            'nombre_transactions': qs.count(),
            'par_type': par_type,
        })
