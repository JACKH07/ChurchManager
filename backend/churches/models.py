from django.db import models # type: ignore from django.db
from django.utils import timezone # type: ignore from django.utils


class SubscriptionPlan(models.TextChoices):
    FREE = 'free', 'Free'
    PRO = 'pro', 'Pro'
    PREMIUM = 'premium', 'Premium'


class Church(models.Model):
    """Tenant SaaS : une organisation (église) isolée des autres."""

    name = models.CharField(max_length=200, verbose_name="Nom de l'organisation")
    email = models.EmailField(verbose_name='Email de contact')
    phone = models.CharField(max_length=30, blank=True, verbose_name='Téléphone')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Église (tenant)'
        verbose_name_plural = 'Églises (tenants)'
        ordering = ['name']

    def __str__(self):
        return self.name


class Subscription(models.Model):
    """Abonnement lié à une église."""

    church = models.ForeignKey(
        Church,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Église',
    )
    plan = models.CharField(
        max_length=20,
        choices=SubscriptionPlan.choices,
        default=SubscriptionPlan.FREE,
    )
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True, verbose_name='Date de fin')
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Abonnement'
        verbose_name_plural = 'Abonnements'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.church} — {self.get_plan_display()}'

    def is_valid_at(self, when=None):
        when = when or timezone.now().date()
        if not self.is_active:
            return False
        if self.end_date and self.end_date < when:
            return False
        return True
