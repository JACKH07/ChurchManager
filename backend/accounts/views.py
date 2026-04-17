from rest_framework import generics, status, viewsets # type: ignore from rest_framework
from rest_framework.decorators import action # type: ignore from rest_framework.decorators
from rest_framework.response import Response # type: ignore from rest_framework.response
from rest_framework.permissions import IsAuthenticated, AllowAny # type: ignore from rest_framework.permissions
from rest_framework_simplejwt.views import TokenObtainPairView # type: ignore from rest_framework_simplejwt.views
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore from rest_framework_simplejwt.tokens
from django.contrib.auth import get_user_model # type: ignore from django.contrib.auth
from drf_spectacular.utils import extend_schema, extend_schema_view # type: ignore from drf_spectacular.utils

from .serializers import (
    CustomTokenObtainPairSerializer, UserSerializer,
    UserCreateSerializer, ChangePasswordSerializer, UserProfileSerializer,
)
from .permissions import IsAdminNational, IsSuperAdmin
from .audit import log_action
from common.tenant import filter_queryset_for_tenant

User = get_user_model()


@extend_schema(tags=['auth'])
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(summary='Connexion utilisateur', description='Authentification par email et mot de passe. Retourne les tokens JWT.')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@extend_schema(tags=['auth'])
class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Déconnexion', description='Invalide le refresh token.')
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'detail': 'Le refresh token est requis.'}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            log_action(request.user, 'logout', 'User', object_id=request.user.pk, request=request)
            return Response({'detail': 'Déconnexion réussie.'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'detail': 'Token invalide ou déjà révoqué.'}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['auth'])
class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


@extend_schema(tags=['auth'])
class ChangePasswordView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    @extend_schema(summary='Changer le mot de passe')
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': 'Mot de passe actuel incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Mot de passe modifié avec succès.'})


@extend_schema(tags=['auth'])
@extend_schema_view(
    list=extend_schema(summary='Liste des utilisateurs'),
    create=extend_schema(summary='Créer un utilisateur'),
    retrieve=extend_schema(summary='Détail utilisateur'),
    update=extend_schema(summary='Modifier un utilisateur'),
    destroy=extend_schema(summary='Supprimer un utilisateur'),
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('last_name', 'first_name')
    permission_classes = [IsAdminNational]
    filterset_fields = ['role', 'is_active', 'entity_type']
    search_fields = ['email', 'first_name', 'last_name']

    def get_queryset(self):
        qs = super().get_queryset()
        if getattr(self, 'swagger_fake_view', False):
            return qs
        return filter_queryset_for_tenant(qs, self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsSuperAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        current = self.request.user
        if getattr(current, 'church_id', None):
            new_user = serializer.save(church=current.church)
        else:
            new_user = serializer.save()
        log_action(current, 'create_user', 'User',
                   object_id=new_user.pk,
                   details={'email': new_user.email, 'role': new_user.role},
                   request=self.request)

    def perform_destroy(self, instance):
        log_action(self.request.user, 'delete_user', 'User',
                   object_id=instance.pk,
                   details={'email': instance.email},
                   request=self.request)
        instance.delete()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
