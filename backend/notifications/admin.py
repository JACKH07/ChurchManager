from django.contrib import admin  # pyright: ignore[reportMissingImports]
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['titre', 'destinataire', 'type_notification', 'est_lue', 'created_at']
    list_filter = ['type_notification', 'est_lue']
    search_fields = ['titre', 'destinataire__email']
