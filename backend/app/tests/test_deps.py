import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta
import pytest
from fastapi import HTTPException
from core import jwt as jwt_module
from api.v1 import deps
from db.models.user import User


class DummyQuery:
    def __init__(self, user):
        self._user = user
    def filter(self, *args, **kwargs):
        return self
    def first(self):
        return self._user

class DummyDB:
    def __init__(self, user):
        self._user = user
    def query(self, model):
        return DummyQuery(self._user)

def test_get_current_user_valid():
    user = User(id=1, email="test@example.com", hashed_password="hash")
    token = jwt_module.create_access_token({"sub": str(user.id)}, expires_minutes=1)
    db = DummyDB(user)
    result = deps.get_current_user(token=token, db=db)
    assert result == user

def test_get_current_user_invalid_token():
    user = User(id=1, email="a@a.com", hashed_password="h")
    db = DummyDB(user)
    with pytest.raises(HTTPException):
        deps.get_current_user(token="bad.token", db=db)


def test_get_current_user_expired_token():
    user = User(id=1, email="a@a.com", hashed_password="h")
    db = DummyDB(user)
    expired = jwt_module.jwt.encode(
        {"sub": str(user.id), "exp": datetime.utcnow() - timedelta(minutes=1)},
        jwt_module.SECRET_KEY,
        algorithm=jwt_module.ALGORITHM,
    )
    with pytest.raises(HTTPException):
        deps.get_current_user(token=expired, db=db)
