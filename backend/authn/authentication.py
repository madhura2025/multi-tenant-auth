from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from authn.token_service import decode_and_validate_token


class CustomJWTAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = get_authorization_header(request).split()
        if not auth_header:
            return None
        if auth_header[0].decode().lower() != self.keyword.lower():
            return None
        if len(auth_header) != 2:
            raise AuthenticationFailed("Invalid Authorization header format.")

        token = auth_header[1].decode()
        payload = decode_and_validate_token(token, expected_type="access")

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationFailed("Token missing subject.")

        user_model = get_user_model()
        try:
            user = user_model.objects.get(id=user_id, is_active=True)
        except user_model.DoesNotExist as exc:
            raise AuthenticationFailed("User not found or inactive.") from exc

        return (user, payload)
