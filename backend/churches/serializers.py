from rest_framework import serializers # type: ignore from rest_framework

from .models import Church, Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    plan_display = serializers.CharField(source='get_plan_display', read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'church', 'plan', 'plan_display', 'start_date', 'end_date', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChurchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Church
        fields = ['id', 'name', 'email', 'phone', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChurchRegistrationSerializer(serializers.Serializer):
    """Inscription : nouvelle église + premier administrateur."""

    church_name = serializers.CharField(max_length=200)
    church_email = serializers.EmailField()
    church_phone = serializers.CharField(max_length=30, required=False, allow_blank=True)
    admin_email = serializers.EmailField()
    admin_password = serializers.CharField(write_only=True, min_length=8)
    admin_first_name = serializers.CharField(max_length=100)
    admin_last_name = serializers.CharField(max_length=100)
