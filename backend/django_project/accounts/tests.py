import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .forms import PlatformUserForm


@pytest.mark.django_db
def test_platform_user_model_str():
    user = get_user_model().objects.create_user(
        username="john", email="j@x.com", password="pass"
    )
    assert str(user) == "john"
    assert user.role == "user"
    assert user.status == "active"


@pytest.mark.django_db
def test_register_and_login_api():
    client = APIClient()
    resp = client.post(
        reverse("register"),
        {"username": "bob", "email": "b@x.com", "password": "secret"},
    )
    assert resp.status_code == 201
    # Access token is available but we'll test separately
    # Login
    resp = client.post(
        reverse("login"),
        {"username": "bob", "password": "secret"},
    )
    assert resp.status_code == 200
    assert "access" in resp.data
    assert resp.data["user"]["username"] == "bob"


@pytest.mark.django_db
def test_me_endpoint_requires_authentication():
    client = APIClient()
    url = reverse("me")
    resp = client.get(url)
    assert resp.status_code == 401


@pytest.mark.django_db
def test_me_endpoint_with_token():
    client = APIClient()
    reg = client.post(
        reverse("register"),
        {"username": "alice", "email": "a@x.com", "password": "s3cret"},
    )
    token = reg.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    resp = client.get(reverse("me"))
    assert resp.status_code == 200
    assert resp.data["email"] == "a@x.com"


@pytest.mark.django_db
def test_platform_user_form():
    form = PlatformUserForm(
        data={
            "username": "ann",
            "email": "ann@example.com",
            "password": "pwd12345",
        }
    )
    assert form.is_valid()
    user = form.save()
    assert user.check_password("pwd12345")
