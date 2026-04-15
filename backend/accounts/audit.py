"""Utilitaire pour alimenter le journal d'audit (AuditLog)."""
from .models import AuditLog


def log_action(user, action: str, model_name: str, object_id=None, details: dict = None, request=None):
    """
    Enregistre une action dans le journal d'audit.

    Usage:
        log_action(request.user, 'create', 'Fidele', object_id=fidele.pk, request=request)
        log_action(request.user, 'login', 'User', details={'email': user.email}, request=request)
    """
    ip_address = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')

    AuditLog.objects.create(
        user=user if user and user.is_authenticated else None,
        action=action,
        model_name=model_name,
        object_id=str(object_id) if object_id else '',
        details=details or {},
        ip_address=ip_address,
    )
