from django.db import models  # pyright: ignore[reportMissingImports]


class TypeNotification(models.TextChoices):
    INFO = 'info', 'Information'
    ALERTE = 'alerte', 'Alerte'
    RAPPEL = 'rappel', 'Rappel'
    SUCCES = 'succes', 'Succès'


class Notification(models.Model):
    church = models.ForeignKey(
        'churches.Church',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
        verbose_name='Église (tenant)',
    )
    destinataire = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='notifications'
    )
    titre = models.CharField(max_length=200)
    message = models.TextField()
    type_notification = models.CharField(max_length=20, choices=TypeNotification.choices, default=TypeNotification.INFO)
    lien = models.CharField(max_length=500, blank=True, verbose_name='Lien de redirection')
    est_lue = models.BooleanField(default=False, verbose_name='Lue')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titre} → {self.destinataire}"

    def save(self, *args, **kwargs):
        if self.destinataire_id and not self.church_id and getattr(self.destinataire, 'church_id', None):
            self.church_id = self.destinataire.church_id
        super().save(*args, **kwargs)
