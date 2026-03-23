from rest_framework.permissions import BasePermission


class IsTenantMember(BasePermission):
    """
    Ensures JWT tenant_id claim matches authenticated user's tenant.
    """

    def has_permission(self, request, view):
        token_tenant_id = request.auth.get("tenant_id") if request.auth else None
        return request.user.is_authenticated and str(request.user.tenant_id) == str(token_tenant_id)


class HasRole(BasePermission):
    required_role = None

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == self.required_role


class IsAdminRole(HasRole):
    required_role = "admin"
