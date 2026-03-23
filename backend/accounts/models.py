import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    USER = "user", "User"


class TenantUserManager(BaseUserManager):
    def create_user(self, tenant, email, password=None, role=UserRole.USER, **extra_fields):
        if not tenant:
            raise ValueError("tenant is required")
        if not email:
            raise ValueError("email is required")
        email = self.normalize_email(email)
        user = self.model(tenant=tenant, email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, tenant, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(
            tenant=tenant,
            email=email,
            password=password,
            role=UserRole.ADMIN,
            **extra_fields,
        )


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="users",
    )
    email = models.EmailField(max_length=255)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.USER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["tenant"]

    objects = TenantUserManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "email"],
                name="uniq_user_email_per_tenant",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "email"]),
            models.Index(fields=["tenant", "role"]),
        ]

    def __str__(self) -> str:
        return f"{self.email} [{self.tenant_id}]"
