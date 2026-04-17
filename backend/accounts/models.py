from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin # type: ignore from django.contrib.auth.models
from django.db import models # type: ignore from django.db
from django.utils import timezone # type: ignore from django.utils


class UserRole(models.TextChoices):
    SUPER_ADMIN = 'super_admin', 'Super Administrateur'
    ADMIN_NATIONAL = 'admin_national', 'Administrateur National'
    ADMIN_REGION = 'admin_region', 'Administrateur Régional'
    SUPERVISEUR_DISTRICT = 'superviseur_district', 'Superviseur de District'
    CHEF_PAROISSE = 'chef_paroisse', 'Chef de Paroisse'
    PASTEUR_LOCAL = 'pasteur_local', 'Pasteur Local'
    TRESORIER = 'tresorier', 'Trésorier'
    FIDELE = 'fidele', 'Fidèle'


class EntityType(models.TextChoices):
    NATIONAL = 'national', 'National'
    REGION = 'region', 'Région'
    DISTRICT = 'district', 'District'
    PAROISSE = 'paroisse', 'Paroisse'
    EGLISE = 'eglise', 'Église Locale'


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.SUPER_ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    church = models.ForeignKey(
        'churches.Church',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Église (tenant)',
    )
    email = models.EmailField(unique=True, verbose_name='Adresse email')
    first_name = models.CharField(max_length=100, verbose_name='Prénom')
    last_name = models.CharField(max_length=100, verbose_name='Nom')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Téléphone')
    role = models.CharField(max_length=30, choices=UserRole.choices, default=UserRole.FIDELE, verbose_name='Rôle')
    entity_type = models.CharField(max_length=20, choices=EntityType.choices, blank=True, verbose_name="Type d'entité")
    entity_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="ID de l'entité")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def has_role(self, *roles):
        return self.role in roles

    def is_at_least(self, role):
        hierarchy = [
            UserRole.FIDELE,
            UserRole.TRESORIER,
            UserRole.PASTEUR_LOCAL,
            UserRole.CHEF_PAROISSE,
            UserRole.SUPERVISEUR_DISTRICT,
            UserRole.ADMIN_REGION,
            UserRole.ADMIN_NATIONAL,
            UserRole.SUPER_ADMIN,
        ]
        user_level = hierarchy.index(self.role) if self.role in hierarchy else -1
        required_level = hierarchy.index(role) if role in hierarchy else -1
        return user_level >= required_level


class AuditLog(models.Model):
    church = models.ForeignKey(
        'churches.Church',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name='Église',
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=200)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=50, blank=True)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Journal d'audit"
        verbose_name_plural = "Journaux d'audit"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.action} ({self.timestamp})"
