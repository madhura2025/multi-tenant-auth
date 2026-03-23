from django.contrib.auth import authenticate
from rest_framework import serializers

from accounts.models import User, UserRole
from authn.token_service import create_token_pair_for_user
from tenants.models import Tenant


class SignupSerializer(serializers.Serializer):
    tenant_id = serializers.UUIDField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=UserRole.choices, default=UserRole.USER)

    def validate(self, attrs):
        tenant_id = attrs["tenant_id"]
        email = attrs["email"].lower()
        if not Tenant.objects.filter(id=tenant_id, is_active=True).exists():
            raise serializers.ValidationError("Tenant not found or inactive.")
        if User.objects.filter(tenant_id=tenant_id, email__iexact=email).exists():
            raise serializers.ValidationError("User already exists in this tenant.")
        attrs["email"] = email
        return attrs

    def create(self, validated_data):
        tenant = Tenant.objects.get(pk=validated_data["tenant_id"])
        return User.objects.create_user(
            tenant=tenant,
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data["role"],
            is_active=True,
        )


class LoginSerializer(serializers.Serializer):
    tenant_id = serializers.UUIDField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            tenant_id=attrs["tenant_id"],
            email=attrs["email"],
            password=attrs["password"],
        )
        if not user:
            raise serializers.ValidationError("Invalid tenant/email/password.")
        if not user.is_active:
            raise serializers.ValidationError("User is inactive.")
        attrs["user"] = user
        return attrs


def token_response_for_user(user: User):
    return create_token_pair_for_user(user)
