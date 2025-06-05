from datetime import datetime, timedelta
from jose import jwt
from core.config import settings

SECRET_KEY = settings.SECRET_KEY  #
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_minutes: int | None = None):
    """Generate a JWT access token.

    Parameters
    ----------
    data: dict
        Payload to encode in the token.
    expires_minutes: int | None, optional
        Expiration time in minutes. Defaults to ``ACCESS_TOKEN_EXPIRE_MINUTES``.
    """

    to_encode = data.copy()
    minutes = expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.utcnow() + timedelta(minutes=minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
