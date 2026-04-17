from django.apps import AppConfig # type: ignore from django.apps


class ChurchesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'churches'
    verbose_name = 'Églises (tenants)'
