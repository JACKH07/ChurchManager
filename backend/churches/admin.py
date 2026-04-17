from django.contrib import admin  # pyright: ignore[reportMissingImports]

from .models import Church, Subscription


@admin.register(Church)
class ChurchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'church', 'plan', 'is_active', 'start_date', 'end_date')
    list_filter = ('plan', 'is_active')
