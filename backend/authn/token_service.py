import uuid
from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

from authn.models import RevokedToken


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _jwt_config():
    return {
        "algorithm": settings.JWT_ALGORITHM,
        "signing_key": settings.JWT_SIGNING_KEY,
        "issuer": settings.JWT_ISSUER,
        "audience": settings.JWT_AUDIENCE,
    }


def _build_payload(user, token_type: str, lifetime: timedelta) -> dict:
    now = _utc_now()
    return {
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id),
        "role": user.role,
        "type": token_type,
        "jti": uuid.uuid4().hex,
        "iat": int(now.timestamp()),
        "exp": int((now + lifetime).timestamp()),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
    }


def create_token_pair_for_user(user) -> dict:
    access_payload = _build_payload(user, "access", settings.JWT_ACCESS_LIFETIME)
    refresh_payload = _build_payload(user, "refresh", settings.JWT_REFRESH_LIFETIME)
    config = _jwt_config()
    access = jwt.encode(access_payload, config["signing_key"], algorithm=config["algorithm"])
    refresh = jwt.encode(refresh_payload, config["signing_key"], algorithm=config["algorithm"])
    return {
        "access": access,
        "refresh": refresh,
        "user": {
            "id": str(user.id),
            "tenant_id": str(user.tenant_id),
            "email": user.email,
            "role": user.role,
        },
    }


def decode_and_validate_token(token: str, expected_type: str | None = None) -> dict:
    config = _jwt_config()
    try:
        payload = jwt.decode(
            token,
            config["signing_key"],
            algorithms=[config["algorithm"]],
            issuer=config["issuer"],
            audience=config["audience"],
        )
    except jwt.InvalidTokenError as exc:
        raise AuthenticationFailed("Invalid or expired token.") from exc

    token_type = payload.get("type")
    if expected_type and token_type != expected_type:
        raise AuthenticationFailed("Invalid token type.")

    jti = payload.get("jti")
    if not jti:
        raise AuthenticationFailed("Token is missing jti.")
    if RevokedToken.objects.filter(jti=jti).exists():
        raise AuthenticationFailed("Token has been revoked.")

    return payload


def revoke_token_from_payload(payload: dict) -> None:
    exp_timestamp = payload.get("exp")
    if not exp_timestamp:
        return
    RevokedToken.objects.get_or_create(
        jti=payload["jti"],
        defaults={
            "token_type": payload.get("type", "unknown"),
            "expires_at": datetime.fromtimestamp(exp_timestamp, tz=timezone.utc),
        },
    )
