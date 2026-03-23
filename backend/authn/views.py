from rest_framework import permissions, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

from authn.permissions import IsAdminRole, IsTenantMember
from authn.serializers import LoginSerializer, SignupSerializer, token_response_for_user
from authn.token_service import (
    create_token_pair_for_user,
    decode_and_validate_token,
    revoke_token_from_payload,
)
from accounts.models import User


class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(token_response_for_user(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        return Response(token_response_for_user(user), status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            payload = decode_and_validate_token(refresh_token, expected_type="refresh")
            revoke_token_from_payload(payload)
        except AuthenticationFailed:
            return Response({"detail": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            payload = decode_and_validate_token(refresh_token, expected_type="refresh")
            user = User.objects.get(id=payload["sub"], is_active=True)
        except (AuthenticationFailed, User.DoesNotExist):
            return Response({"detail": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)

        revoke_token_from_payload(payload)
        return Response(create_token_pair_for_user(user), status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [IsTenantMember]

    def get(self, request):
        user = request.user
        return Response(
            {
                "id": str(user.id),
                "tenant_id": str(user.tenant_id),
                "email": user.email,
                "role": user.role,
            }
        )


class AdminOnlyView(APIView):
    permission_classes = [IsTenantMember, IsAdminRole]

    def get(self, request):
        return Response(
            {
                "message": "Only admin users of this tenant can access this endpoint.",
                "tenant_id": str(request.user.tenant_id),
            }
        )
