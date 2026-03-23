from django.contrib.auth.backends import BaseBackend

from accounts.models import User


class TenantEmailBackend(BaseBackend):
    def authenticate(self, request, tenant_id=None, email=None, password=None, **kwargs):
        if not tenant_id or not email or not password:
            return None
        try:
            user = User.objects.select_related("tenant").get(
                tenant_id=tenant_id,
                email__iexact=email,
            )
        except User.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
