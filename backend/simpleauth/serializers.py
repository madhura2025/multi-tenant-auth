from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User


class SimpleLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs["email"].lower()
        password = attrs["password"]

        users = list(User.objects.filter(email__iexact=email, is_active=True).select_related("tenant"))
        if not users:
            raise serializers.ValidationError("Invalid email or password.")
        if len(users) > 1:
            raise serializers.ValidationError(
                "Multiple accounts found for this email across tenants. Use tenant login endpoint."
            )

        user = users[0]
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")
        attrs["user"] = user
        return attrs


def simple_token_response_for_user(user: User):
    refresh = RefreshToken.for_user(user)
    refresh["tenant_id"] = str(user.tenant_id)
    refresh["role"] = user.role
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "id": str(user.id),
            "tenant_id": str(user.tenant_id),
            "email": user.email,
            "role": user.role,
        },
    }
