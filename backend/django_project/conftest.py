import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

@pytest.fixture
def admin_user(db):
    User = get_user_model()
    user = User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="adminpass",
        role="platform_admin",
        is_staff=True,
    )
    return user

@pytest.fixture
def auth_client(admin_user):
    client = APIClient()
    resp = client.post(reverse("login"), {"username": admin_user.username, "password": "adminpass"})
    token = resp.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client
