"""Provisionnement d'un tenant (National + abonnement par défaut)."""

from django.db import transaction # type: ignore from django.db

from .models import Church, Subscription, SubscriptionPlan


def provision_new_church(church: Church) -> None:
    """
    Crée l'enregistrement National racine et un abonnement Free si absents.
    À appeler après création d'une Church (inscription SaaS ou migration).
    """
    from hierarchy.models import National

    with transaction.atomic():
        if not National.objects.filter(church=church).exists():
            National.objects.create(
                church=church,
                nom=church.name,
                pays='',
                email=church.email or '',
                telephone=church.phone or '',
            )
        if not Subscription.objects.filter(church=church).exists():
            Subscription.objects.create(
                church=church,
                plan=SubscriptionPlan.FREE,
                is_active=True,
            )
