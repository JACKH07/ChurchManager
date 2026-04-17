from django.db import transaction # type: ignore from django.db
from rest_framework import viewsets, status # type: ignore from rest_framework
from rest_framework.decorators import action # type: ignore from rest_framework.decorators
from rest_framework.permissions import AllowAny, IsAuthenticated # type: ignore from rest_framework.permissions
from rest_framework.response import Response # type: ignore from rest_framework.response
from rest_framework.views import APIView # type: ignore from rest_framework.views
from drf_spectacular.utils import extend_schema # type: ignore from drf_spectacular.utils

from accounts.models import User, UserRole
from accounts.permissions import IsSuperAdmin
from accounts.serializers import UserSerializer
from common.tenant import filter_queryset_for_tenant
from .models import Church, Subscription
from .serializers import ChurchSerializer, SubscriptionSerializer, ChurchRegistrationSerializer
from .services import provision_new_church


@extend_schema(tags=['churches'])
class RegisterChurchView(APIView):
    """Crée une église (tenant), l'organisation nationale par défaut, l'abonnement Free et l'admin."""

    permission_classes = [AllowAny]

    @extend_schema(summary="Inscription d'une nouvelle église")
    def post(self, request):
        ser = ChurchRegistrationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        if User.objects.filter(email=d['admin_email']).exists():
            return Response({'admin_email': 'Un compte existe déjà avec cet email.'}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            church = Church.objects.create(
                name=d['church_name'],
                email=d['church_email'],
                phone=d.get('church_phone') or '',
            )
            provision_new_church(church)
            user = User.objects.create_user(
                email=d['admin_email'],
                password=d['admin_password'],
                first_name=d['admin_first_name'],
                last_name=d['admin_last_name'],
                role=UserRole.ADMIN_NATIONAL,
                church=church,
            )
        return Response(
            {
                'church': ChurchSerializer(church).data,
                'user': UserSerializer(user).data,
                'detail': 'Organisation créée. Vous pouvez vous connecter.',
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=['churches'])
class ChurchViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChurchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Church.objects.all().order_by('name')
        if getattr(self, 'swagger_fake_view', False):
            return qs
        user = self.request.user
        if getattr(user, 'role', None) == UserRole.SUPER_ADMIN and not getattr(user, 'church_id', None):
            return qs
        if user.church_id:
            return qs.filter(pk=user.church_id)
        return qs.none()


@extend_schema(tags=['churches'])
class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Subscription.objects.select_related('church').order_by('-created_at')
        if getattr(self, 'swagger_fake_view', False):
            return qs
        return filter_queryset_for_tenant(qs, self.request.user)

    @action(detail=False, methods=['get'], url_path='current')
    def current(self, request):
        """Abonnement le plus récent de l'église connectée."""
        if not request.user.church_id:
            return Response({'detail': 'Aucune église.'}, status=400)
        sub = (
            Subscription.objects.filter(church_id=request.user.church_id)
            .order_by('-created_at')
            .first()
        )
        if not sub:
            return Response({'detail': 'Aucun abonnement.'}, status=404)
        return Response(SubscriptionSerializer(sub).data)


@extend_schema(tags=['churches'])
class PlatformChurchViewSet(viewsets.ModelViewSet):
    """Gestion des tenants (SuperAdmin plateforme uniquement)."""

    queryset = Church.objects.all().order_by('-created_at')
    serializer_class = ChurchSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Church.objects.none()
        return Church.objects.all().order_by('-created_at')
