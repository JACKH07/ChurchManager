from django.db import models # type: ignore from django.db
from django.utils import timezone # type: ignore from django.utils
from hierarchy.models import EgliseLocale


class StatutFidele(models.TextChoices):
    ACTIF = 'actif', 'Actif'
    INACTIF = 'inactif', 'Inactif'
    TRANSFERE = 'transfere', 'Transféré'
    DECEDE = 'decede', 'Décédé'


class SituationFamiliale(models.TextChoices):
    CELIBATAIRE = 'celibataire', 'Célibataire'
    MARIE = 'marie', 'Marié(e)'
    DIVORCE = 'divorce', 'Divorcé(e)'
    VEUF = 'veuf', 'Veuf/Veuve'


class Genre(models.TextChoices):
    HOMME = 'H', 'Homme'
    FEMME = 'F', 'Femme'
    AUTRE = 'A', 'Autre'


def generate_code_fidele(eglise: EgliseLocale, annee: int = None) -> str:
    """Génère le code unique d'identification du fidèle : REG-DIS-PAR-EGL-XXXX-AAAA"""
    if annee is None:
        annee = timezone.now().year
    p = eglise.paroisse
    d = p.district
    r = d.region
    # Compter les fidèles existants dans cette église
    count = Fidele.objects.filter(eglise=eglise).count() + 1
    seq = str(count).zfill(4)
    return f"{r.code}-{d.code}-{p.code}-{eglise.code}-{seq}-{annee}"


class Ministere(models.Model):
    nom = models.CharField(max_length=100, verbose_name='Nom du ministère')
    description = models.TextField(blank=True)
    eglise = models.ForeignKey(EgliseLocale, on_delete=models.CASCADE, related_name='ministeres')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ministère / Groupe'
        verbose_name_plural = 'Ministères / Groupes'
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} - {self.eglise.nom}"


class Fidele(models.Model):
    code_fidele = models.CharField(max_length=30, unique=True, verbose_name='Code d\'identification', editable=False)
    nom = models.CharField(max_length=100, verbose_name='Nom')
    prenom = models.CharField(max_length=100, verbose_name='Prénom')
    genre = models.CharField(max_length=1, choices=Genre.choices, verbose_name='Genre')
    date_naissance = models.DateField(null=True, blank=True, verbose_name='Date de naissance')
    lieu_naissance = models.CharField(max_length=200, blank=True, verbose_name='Lieu de naissance')
    photo = models.ImageField(upload_to='fideles/photos/', null=True, blank=True)
    situation_familiale = models.CharField(
        max_length=20, choices=SituationFamiliale.choices,
        default=SituationFamiliale.CELIBATAIRE, verbose_name='Situation familiale'
    )
    nombre_enfants = models.PositiveSmallIntegerField(default=0, verbose_name='Nombre d\'enfants')
    telephone = models.CharField(max_length=20, blank=True)
    telephone_2 = models.CharField(max_length=20, blank=True, verbose_name='Téléphone secondaire')
    email = models.EmailField(blank=True)
    adresse = models.TextField(blank=True, verbose_name='Adresse')
    profession = models.CharField(max_length=100, blank=True, verbose_name='Profession')
    eglise = models.ForeignKey(EgliseLocale, on_delete=models.CASCADE, related_name='fideles', verbose_name='Église locale')
    ministeres = models.ManyToManyField(Ministere, blank=True, related_name='membres', verbose_name='Ministères')
    statut = models.CharField(max_length=20, choices=StatutFidele.choices, default=StatutFidele.ACTIF)
    date_inscription = models.DateField(default=timezone.now, verbose_name='Date d\'inscription')
    date_bapteme = models.DateField(null=True, blank=True, verbose_name='Date de baptême')
    notes = models.TextField(blank=True, verbose_name='Notes internes')
    user = models.OneToOneField(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='fidele_profile', verbose_name='Compte utilisateur lié'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Fidèle'
        verbose_name_plural = 'Fidèles'
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.nom} {self.prenom} [{self.code_fidele}]"

    def save(self, *args, **kwargs):
        if not self.code_fidele:
            self.code_fidele = generate_code_fidele(self.eglise, self.date_inscription.year)
        super().save(*args, **kwargs)

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    @property
    def age(self):
        if self.date_naissance:
            today = timezone.now().date()
            return today.year - self.date_naissance.year - (
                (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day)
            )
        return None


class TransfertFidele(models.Model):
    fidele = models.ForeignKey(Fidele, on_delete=models.CASCADE, related_name='transferts')
    eglise_origine = models.ForeignKey(EgliseLocale, on_delete=models.CASCADE, related_name='transferts_sortants')
    eglise_destination = models.ForeignKey(EgliseLocale, on_delete=models.CASCADE, related_name='transferts_entrants')
    date_transfert = models.DateField(default=timezone.now)
    motif = models.TextField(blank=True, verbose_name='Motif du transfert')
    approuve_par = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True,
        related_name='transferts_approuves'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Transfert de fidèle'
        verbose_name_plural = 'Transferts de fidèles'
        ordering = ['-date_transfert']

    def __str__(self):
        return f"Transfert de {self.fidele} : {self.eglise_origine} → {self.eglise_destination}"
