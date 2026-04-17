from django.db import models # type: ignore from django.db
from django.utils import timezone # type: ignore from django.utils
import uuid # type: ignore from uuid


class TypeCotisation(models.TextChoices):
    MENSUELLE_MEMBRE = 'mensuelle_membre', 'Cotisation mensuelle membre'
    DIME = 'dime', 'Dîme'
    OFFRANDE = 'offrande', 'Offrande'
    CONTRIBUTION_PAROISSE = 'contribution_paroisse', 'Contribution Paroisse'
    CONTRIBUTION_DISTRICT = 'contribution_district', 'Contribution District'
    CONTRIBUTION_REGION = 'contribution_region', 'Contribution Région'
    COTISATION_NATIONALE = 'cotisation_nationale', 'Cotisation Nationale'
    DON_SPECIAL = 'don_special', 'Don Spécial'
    PROJET = 'projet', 'Projet Spécial'


class ModePaiement(models.TextChoices):
    ESPECES = 'especes', 'Espèces'
    WAVE = 'wave', 'Wave'
    ORANGE_MONEY = 'orange_money', 'Orange Money'
    MTN_MOMO = 'mtn_momo', 'MTN MoMo'
    VIREMENT = 'virement', 'Virement bancaire'
    CHEQUE = 'cheque', 'Chèque'


class StatutPaiement(models.TextChoices):
    EN_ATTENTE = 'en_attente', 'En attente'
    VALIDE = 'valide', 'Validé'
    REJETE = 'rejete', 'Rejeté'
    REMBOURSE = 'rembourse', 'Remboursé'


class NiveauEntite(models.TextChoices):
    FIDELE = 'fidele', 'Fidèle'
    EGLISE = 'eglise', 'Église Locale'
    PAROISSE = 'paroisse', 'Paroisse'
    DISTRICT = 'district', 'District'
    REGION = 'region', 'Région'
    NATIONAL = 'national', 'National'


class Cotisation(models.Model):
    church = models.ForeignKey(
        'churches.Church',
        on_delete=models.CASCADE,
        related_name='cotisations',
        null=True,
        blank=True,
        verbose_name='Église (tenant)',
    )
    reference = models.CharField(max_length=20, unique=True, editable=False, verbose_name='Référence')
    fidele = models.ForeignKey(
        'members.Fidele', on_delete=models.CASCADE, null=True, blank=True,
        related_name='cotisations', verbose_name='Fidèle'
    )
    # Pour les cotisations d'entités (paroisse → district, etc.)
    niveau_entite = models.CharField(max_length=20, choices=NiveauEntite.choices, blank=True)
    entite_id = models.PositiveIntegerField(null=True, blank=True)

    type_cotisation = models.CharField(max_length=30, choices=TypeCotisation.choices)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    devise = models.CharField(max_length=3, default='XOF')
    periode_mois = models.PositiveSmallIntegerField(null=True, blank=True, help_text='Mois concerné (1-12)')
    periode_annee = models.PositiveSmallIntegerField(null=True, blank=True, help_text='Année concernée')
    mode_paiement = models.CharField(max_length=20, choices=ModePaiement.choices, default=ModePaiement.ESPECES)
    statut = models.CharField(max_length=20, choices=StatutPaiement.choices, default=StatutPaiement.EN_ATTENTE)
    notes = models.TextField(blank=True)
    date_paiement = models.DateTimeField(default=timezone.now)
    enregistre_par = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True,
        related_name='cotisations_enregistrees'
    )
    valide_par = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='cotisations_validees'
    )
    date_validation = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name='ID transaction Mobile Money')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cotisation'
        verbose_name_plural = 'Cotisations'
        ordering = ['-date_paiement']

    def __str__(self):
        source = self.fidele.nom_complet if self.fidele else f"Entité {self.niveau_entite} #{self.entite_id}"
        return f"{self.reference} - {source} - {self.montant} {self.devise}"

    def save(self, *args, **kwargs):
        if self.fidele_id and not self.church_id and self.fidele.church_id:
            self.church_id = self.fidele.church_id
        if not self.reference:
            self.reference = self._generate_reference()
        super().save(*args, **kwargs)

    def _generate_reference(self):
        year = timezone.now().year
        month = timezone.now().month
        import random
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        return f"COT-{year}{month:02d}-{suffix}"


class Recu(models.Model):
    church = models.ForeignKey(
        'churches.Church',
        on_delete=models.CASCADE,
        related_name='recus',
        null=True,
        blank=True,
        verbose_name='Église (tenant)',
    )
    cotisation = models.OneToOneField(Cotisation, on_delete=models.CASCADE, related_name='recu')
    numero_recu = models.CharField(max_length=20, unique=True)
    genere_le = models.DateTimeField(auto_now_add=True)
    genere_par = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    fichier_pdf = models.FileField(upload_to='recus/', null=True, blank=True)

    class Meta:
        verbose_name = 'Reçu'
        verbose_name_plural = 'Reçus'

    def __str__(self):
        return f"Reçu {self.numero_recu} - {self.cotisation.reference}"

    def save(self, *args, **kwargs):
        if self.cotisation_id and not self.church_id and self.cotisation.church_id:
            self.church_id = self.cotisation.church_id
        super().save(*args, **kwargs)


class ObjectifCotisation(models.Model):
    church = models.ForeignKey(
        'churches.Church',
        on_delete=models.CASCADE,
        related_name='objectifs_cotisation',
        null=True,
        blank=True,
        verbose_name='Église (tenant)',
    )
    """Objectifs de collecte par période"""
    niveau_entite = models.CharField(max_length=20, choices=NiveauEntite.choices)
    entite_id = models.PositiveIntegerField()
    type_cotisation = models.CharField(max_length=30, choices=TypeCotisation.choices)
    montant_objectif = models.DecimalField(max_digits=12, decimal_places=2)
    periode_mois = models.PositiveSmallIntegerField()
    periode_annee = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Objectif de cotisation'
        constraints = [
            models.UniqueConstraint(
                fields=['church', 'niveau_entite', 'entite_id', 'type_cotisation', 'periode_mois', 'periode_annee'],
                name='contrib_objectif_church_periode_uniq',
            ),
        ]
