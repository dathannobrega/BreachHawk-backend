from rest_framework.permissions import BasePermission

from .models import PlatformUser


class IsPlatformAdmin(BasePermission):
    """Allows access only to platform admin users."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == PlatformUser.Role.PLATFORM_ADMIN
        )


class IsAdminOrPlatformAdmin(BasePermission):
    """Allow staff or platform admin users."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (
                user.is_staff
                or user.role == PlatformUser.Role.PLATFORM_ADMIN
            )
        )
