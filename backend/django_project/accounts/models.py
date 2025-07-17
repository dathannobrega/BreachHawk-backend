from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class PlatformUser(AbstractUser):
    """Custom user model extending Django's ``AbstractUser``."""

    class Role(models.TextChoices):
        USER = "user", "User"
        ADMIN = "admin", "Admin"
        PLATFORM_ADMIN = "platform_admin", "Platform Admin"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        SUSPENDED = "suspended", "Suspended"

    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.USER
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    company = models.CharField(max_length=255, blank=True, null=True)
    job_title = models.CharField(max_length=255, blank=True, null=True)
    is_subscribed = models.BooleanField(default=True)
    profile_image = models.CharField(max_length=255, blank=True, null=True)
    organization = models.CharField(max_length=255, blank=True, null=True)
    contact = models.CharField(max_length=255, blank=True, null=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    lockout_until = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        return self.username or self.email


class LoginHistory(models.Model):
    """Record of user logins."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    device = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    success = models.BooleanField()

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return f"{self.user} @ {self.timestamp}"


class UserSession(models.Model):
    """Stores active authentication sessions."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    token = models.CharField(max_length=255)
    device = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return f"{self.user} - {self.token}"


class PasswordPolicy(models.Model):
    """Defines global password requirements."""

    min_length = models.PositiveIntegerField()
    require_uppercase = models.BooleanField()
    require_lowercase = models.BooleanField()
    require_numbers = models.BooleanField()
    require_symbols = models.BooleanField()

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return f"Policy {self.id}"


class PasswordResetToken(models.Model):
    """Token used for password reset flow."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return f"{self.user} - {self.token}"


class UserSearchQuota(models.Model):
    """Tracks how many search requests a user can perform."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="search_quota",
    )
    remaining = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return f"{self.user} - {self.remaining}"
