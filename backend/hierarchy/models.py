from django.db import models # type: ignore from django.db
from django.conf import settings # type: ignore from django.conf


class National(models.Model):
    nom = models.CharField(max_length=200, verbose_name='Nom de l\'organisation')
    pays = models.CharField(max_length=100, verbose_name='Pays')
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    date_fondation = models.DateField(null=True, blank=True, verbose_name='Date de fondation')
    adresse = models.TextField(blank=True, verbose_name='Adresse du siège')
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    site_web = models.URLField(blank=True, verbose_name='Site web')
    description = models.TextField(blank=True)
    couleur_primaire = models.CharField(max_length=7, default='#1e40af', verbose_name='Couleur primaire (hex)')
    couleur_secondaire = models.CharField(max_length=7, default='#7c3aed', verbose_name='Couleur secondaire (hex)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Organisation Nationale'
        verbose_name_plural = 'Organisations Nationales'

    def __str__(self):
        return self.nom


class Region(models.Model):
    national = models.ForeignKey(National, on_delete=models.CASCADE, related_name='regions')
    code = models.CharField(max_length=2, unique=True, verbose_name='Code région (2 lettres)')
    nom = models.CharField(max_length=200, verbose_name='Nom de la région')
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='regions_dirigees',
        verbose_name='Responsable régional'
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Région'
        verbose_name_plural = 'Régions'
        ordering = ['nom']

    def __str__(self):
        return f"[{self.code}] {self.nom}"


class District(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='districts')
    code = models.CharField(max_length=2, verbose_name='Code district')
    nom = models.CharField(max_length=200, verbose_name='Nom du district')
    superviseur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='districts_supervises',
        verbose_name='Superviseur de district'
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'District'
        verbose_name_plural = 'Districts'
        ordering = ['nom']
        unique_together = [['region', 'code']]

    def __str__(self):
        return f"[{self.region.code}-{self.code}] {self.nom}"

    @property
    def code_complet(self):
        return f"{self.region.code}-{self.code}"


class Paroisse(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='paroisses')
    code = models.CharField(max_length=3, verbose_name='Code paroisse (3 chiffres)')
    nom = models.CharField(max_length=200, verbose_name='Nom de la paroisse')
    chef = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='paroisses_dirigees',
        verbose_name='Chef de paroisse'
    )
    adresse = models.TextField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Paroisse'
        verbose_name_plural = 'Paroisses'
        ordering = ['nom']
        unique_together = [['district', 'code']]

    def __str__(self):
        return f"{self.nom} ({self.district.code_complet}-{self.code})"


class EgliseLocale(models.Model):
    paroisse = models.ForeignKey(Paroisse, on_delete=models.CASCADE, related_name='eglises')
    code = models.CharField(max_length=3, verbose_name='Code église (3 chiffres)')
    nom = models.CharField(max_length=200, verbose_name='Nom de l\'église locale')
    pasteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='eglises_dirigees',
        verbose_name='Pasteur / Responsable local'
    )
    adresse = models.TextField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    capacite = models.PositiveIntegerField(null=True, blank=True, verbose_name='Capacité d\'accueil')
    date_creation = models.DateField(null=True, blank=True, verbose_name='Date de création')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Église Locale'
        verbose_name_plural = 'Églises Locales'
        ordering = ['nom']
        unique_together = [['paroisse', 'code']]

    def __str__(self):
        return f"{self.nom} ({self.code_complet})"

    @property
    def code_complet(self):
        d = self.paroisse.district
        r = d.region
        return f"{r.code}-{d.code}-{self.paroisse.code}-{self.code}"
