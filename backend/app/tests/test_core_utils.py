import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from core import token_utils, security, jwt as jwt_module


def test_generate_and_verify_unsubscribe_token():
    user_id = 42
    token = token_utils.generate_unsubscribe_token(user_id)
    assert isinstance(token, str)
    retrieved = token_utils.verify_unsubscribe_token(token)
    assert retrieved == user_id


def test_password_hashing_and_verification():
    password = "s3cret!"
    hashed = security.get_password_hash(password)
    assert hashed != password
    assert security.verify_password(password, hashed)
    assert not security.verify_password("wrong", hashed)


def test_create_access_token_contains_data():
    payload = {"sub": "user@example.com"}
    token = jwt_module.create_access_token(payload)
    decoded = jwt_module.jwt.decode(
        token, jwt_module.SECRET_KEY, algorithms=[jwt_module.ALGORITHM]
    )
    assert decoded["sub"] == "user@example.com"
    assert "exp" in decoded


def test_create_access_token_custom_expiry():
    payload = {"sub": "42"}
    token = jwt_module.create_access_token(payload, expires_minutes=60)
    decoded = jwt_module.jwt.decode(
        token, jwt_module.SECRET_KEY, algorithms=[jwt_module.ALGORITHM]
    )
    assert decoded["sub"] == "42"
    exp = datetime.utcfromtimestamp(decoded["exp"])
    remaining = (exp - datetime.utcnow()).total_seconds() / 60
    assert 59 <= remaining <= 60
