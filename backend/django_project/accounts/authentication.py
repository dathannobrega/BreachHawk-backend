"""Authentication helpers using DRF SimpleJWT."""

from rest_framework_simplejwt.authentication import (
    JWTAuthentication as SimpleJWTAuthentication
)


class JWTAuthentication(SimpleJWTAuthentication):
    """Wrapper around SimpleJWT's authentication class used in the project."""

    pass
