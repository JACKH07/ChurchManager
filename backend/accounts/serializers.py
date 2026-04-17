from rest_framework import serializers # type: ignore from rest_framework
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer # type: ignore from rest_framework_simplejwt.serializers 
from django.contrib.auth import get_user_model # type: ignore from django.contrib.auth
from django.contrib.auth.password_validation import validate_password # type: ignore from django.contrib.auth.password_validation

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['full_name'] = user.full_name
        token['role'] = user.role
        token['entity_type'] = user.entity_type
        token['entity_id'] = user.entity_id
        if getattr(user, 'church_id', None):
            token['church_id'] = user.church_id
            from churches.models import Subscription

            sub = (
                Subscription.objects.filter(church_id=user.church_id, is_active=True)
                .order_by('-created_at')
                .first()
            )
            token['subscription_plan'] = sub.plan if sub else 'free'
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'role', 'entity_type', 'entity_id', 'church',
            'is_active', 'date_joined', 'last_login', 'avatar',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'church']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone',
            'role', 'entity_type', 'entity_id',
            'password', 'password_confirm',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password': 'Les mots de passe ne correspondent pas.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password': 'Les mots de passe ne correspondent pas.'})
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'phone', 'avatar', 'role', 'church']
        read_only_fields = ['id', 'email', 'role', 'church']
