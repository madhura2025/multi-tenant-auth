from django.db import models


class RevokedToken(models.Model):
    jti = models.CharField(max_length=64, unique=True)
    token_type = models.CharField(max_length=20)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["jti"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.token_type}:{self.jti}"
