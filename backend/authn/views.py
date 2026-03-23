from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from authn.permissions import IsAdminRole, IsTenantMember
from authn.serializers import LoginSerializer, SignupSerializer, token_response_for_user


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
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({"detail": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


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
