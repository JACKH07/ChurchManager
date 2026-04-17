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


def _church_id(request):
    return getattr(request.user, 'church_id', None)


@extend_schema(tags=['dashboard'])
class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cid = _church_id(request)
        now = timezone.now()
        mois_courant = now.month
        annee_courante = now.year

        fideles = Fidele.objects.filter(statut='actif')
        regions = Region.objects.all()
        districts = District.objects.all()
        paroisses = Paroisse.objects.all()
        eglises = EgliseLocale.objects.all()
        cotisations = Cotisation.objects.all()
        evenements = Evenement.objects.all()
        if cid:
            fideles = fideles.filter(church_id=cid)
            regions = regions.filter(church_id=cid)
            districts = districts.filter(church_id=cid)
            paroisses = paroisses.filter(church_id=cid)
            eglises = eglises.filter(church_id=cid)
            cotisations = cotisations.filter(church_id=cid)
            evenements = evenements.filter(church_id=cid)

        stats = {
            'total_fideles': fideles.count(),
            'total_regions': regions.count(),
            'total_districts': districts.count(),
            'total_paroisses': paroisses.count(),
            'total_eglises': eglises.count(),
            'nouveaux_fideles_mois': fideles.filter(
                date_inscription__month=mois_courant,
                date_inscription__year=annee_courante,
            ).count(),
        }

        cotisations_mois = cotisations.filter(
            statut='valide',
            periode_mois=mois_courant,
            periode_annee=annee_courante,
        )
        stats['recettes_mois'] = float(
            cotisations_mois.aggregate(total=db_models.Sum('montant'))['total'] or 0
        )
        stats['nombre_paiements_mois'] = cotisations_mois.count()

        MOIS = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        evolution = []
        for i in range(5, -1, -1):
            m = (mois_courant - i - 1) % 12 + 1
            a = annee_courante if mois_courant - i > 0 else annee_courante - 1
            qcm = cotisations.filter(statut='valide', periode_mois=m, periode_annee=a)
            montant = qcm.aggregate(total=db_models.Sum('montant'))['total'] or 0
            evolution.append({'mois': MOIS[m - 1], 'montant': float(montant), 'annee': a})
        stats['evolution_cotisations'] = evolution

        repartition_regions = []
        for region in regions:
            total = fideles.filter(eglise__paroisse__district__region=region).count()
            repartition_regions.append({'region': region.nom, 'code': region.code, 'total': total})
        stats['repartition_regions'] = repartition_regions

        total_fideles_actifs = fideles.count()
        fideles_ayant_paye = cotisations.filter(
            type_cotisation='mensuelle_membre',
            statut='valide',
            periode_mois=mois_courant,
            periode_annee=annee_courante,
        ).values('fidele').distinct().count()
        stats['taux_cotisation_mois'] = round(
            (fideles_ayant_paye / total_fideles_actifs * 100) if total_fideles_actifs > 0 else 0, 1
        )

        stats['evenements_a_venir'] = evenements.filter(date_debut__gte=now).count()

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
        cid = _church_id(request)
        eglise_id = request.query_params.get('eglise')
        statut = request.query_params.get('statut', 'actif')
        qs = Fidele.objects.filter(statut=statut)
        if cid:
            qs = qs.filter(church_id=cid)
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
        cid = _church_id(request)
        mois = int(request.query_params.get('mois', timezone.now().month))
        annee = int(request.query_params.get('annee', timezone.now().year))
        eglise_id = request.query_params.get('eglise')

        qs = Cotisation.objects.filter(statut='valide', periode_mois=mois, periode_annee=annee)
        if cid:
            qs = qs.filter(church_id=cid)
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
