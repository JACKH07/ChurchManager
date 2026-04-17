from django.db import models # type: ignore from django.db
from django.utils import timezone # type: ignore from django.utils
from accounts.models import UserRole


class NiveauVisibilite(models.TextChoices):
    NATIONAL = 'national', 'National'
    REGION = 'region', 'Région'
    DISTRICT = 'district', 'District'
    PAROISSE = 'paroisse', 'Paroisse'
    EGLISE = 'eglise', 'Église Locale'


class TypeEvenement(models.TextChoices):
    CONVENTION = 'convention', 'Convention'
    CONFERENCE = 'conference', 'Conférence'
    RETRAITE = 'retraite', 'Retraite spirituelle'
    CULTE_SPECIAL = 'culte_special', 'Culte spécial'
    FORMATION = 'formation', 'Formation / Discipulat'
    REUNION = 'reunion', 'Réunion'
    AUTRE = 'autre', 'Autre'


class Evenement(models.Model):
    church = models.ForeignKey(
        'churches.Church',
        on_delete=models.CASCADE,
        related_name='evenements',
        null=True,
        blank=True,
        verbose_name='Église (tenant)',
    )
    titre = models.CharField(max_length=300, verbose_name='Titre')
    description = models.TextField(blank=True)
    type_evenement = models.CharField(max_length=30, choices=TypeEvenement.choices, default=TypeEvenement.AUTRE)
    date_debut = models.DateTimeField(verbose_name='Date de début')
    date_fin = models.DateTimeField(null=True, blank=True, verbose_name='Date de fin')
    lieu = models.CharField(max_length=300, blank=True, verbose_name='Lieu')
    adresse = models.TextField(blank=True)
    capacite_max = models.PositiveIntegerField(null=True, blank=True, verbose_name='Capacité maximale')
    niveau_visibilite = models.CharField(max_length=20, choices=NiveauVisibilite.choices, default=NiveauVisibilite.EGLISE)
    entite_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="ID de l'entité organisatrice")
    inscription_requise = models.BooleanField(default=False, verbose_name='Inscription requise')
    est_public = models.BooleanField(default=True, verbose_name='Visible par tous')
    image = models.ImageField(upload_to='evenements/', null=True, blank=True)
    createur = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='evenements_crees')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Événement'
        verbose_name_plural = 'Événements'
        ordering = ['date_debut']

    def __str__(self):
        return f"{self.titre} ({self.date_debut.strftime('%d/%m/%Y')})"

    def save(self, *args, **kwargs):
        if self.createur_id and not self.church_id and getattr(self.createur, 'church_id', None):
            self.church_id = self.createur.church_id
        super().save(*args, **kwargs)

    @property
    def places_disponibles(self):
        if self.capacite_max:
            return self.capacite_max - self.inscriptions.filter(statut='confirme').count()
        return None

    @property
    def est_passe(self):
        return self.date_debut < timezone.now()


class InscriptionEvenement(models.Model):
    church = models.ForeignKey(
        'churches.Church',
        on_delete=models.CASCADE,
        related_name='inscriptions_evenements',
        null=True,
        blank=True,
        verbose_name='Église (tenant)',
    )
    class StatutInscription(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente'
        CONFIRME = 'confirme', 'Confirmé'
        ANNULE = 'annule', 'Annulé'
        PRESENT = 'present', 'Présent'

    evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE, related_name='inscriptions')
    fidele = models.ForeignKey('members.Fidele', on_delete=models.CASCADE, related_name='inscriptions_evenements')
    statut = models.CharField(max_length=20, choices=StatutInscription.choices, default=StatutInscription.EN_ATTENTE)
    date_inscription = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Inscription à un événement'
        verbose_name_plural = 'Inscriptions aux événements'
        unique_together = [['evenement', 'fidele']]
        ordering = ['-date_inscription']

    def __str__(self):
        return f"{self.fidele.nom_complet} → {self.evenement.titre}"

    def save(self, *args, **kwargs):
        if self.evenement_id and not self.church_id and self.evenement.church_id:
            self.church_id = self.evenement.church_id
        super().save(*args, **kwargs)


class Annonce(models.Model):
    church = models.ForeignKey(
        'churches.Church',
        on_delete=models.CASCADE,
        related_name='annonces',
        null=True,
        blank=True,
        verbose_name='Église (tenant)',
    )
    titre = models.CharField(max_length=300)
    contenu = models.TextField()
    niveau_visibilite = models.CharField(max_length=20, choices=NiveauVisibilite.choices)
    entite_id = models.PositiveIntegerField(null=True, blank=True)
    est_epingle = models.BooleanField(default=False, verbose_name='Épinglé')
    date_expiration = models.DateField(null=True, blank=True, verbose_name="Date d'expiration")
    auteur = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='annonces')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Annonce'
        verbose_name_plural = 'Annonces'
        ordering = ['-est_epingle', '-created_at']

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        if self.auteur_id and not self.church_id and getattr(self.auteur, 'church_id', None):
            self.church_id = self.auteur.church_id
        super().save(*args, **kwargs)

    @property
    def est_expiree(self):
        if self.date_expiration:
            return self.date_expiration < timezone.now().date()
        return False
