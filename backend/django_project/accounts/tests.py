import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.conf import settings
from django.contrib.auth import get_user_model
from datetime import datetime, timezone, timedelta
from .forms import PlatformUserForm
from .models import PlatformUser, PasswordPolicy, PasswordResetToken


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
def test_update_me_endpoint():
    client = APIClient()
    reg = client.post(
        reverse("register"),
        {"username": "jim", "email": "j@x.com", "password": "s3cret"},
    )
    token = reg.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    resp = client.put(
        reverse("me"),
        {"first_name": "Jim", "last_name": "Beam"},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.data["first_name"] == "Jim"


@pytest.mark.django_db
def test_profile_image_upload_endpoint(tmp_path):
    client = APIClient()
    reg = client.post(
        reverse("register"),
        {"username": "kelly", "email": "k@x.com", "password": "s3cret"},
    )
    token = reg.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    img_file = tmp_path / "img.png"
    img_file.write_bytes(b"fakeimg")
    with img_file.open("rb") as f:
        resp = client.post(
            reverse("profile-image"), {"file": f}, format="multipart"
        )
    assert resp.status_code == 200
    assert resp.data["profile_image"].startswith("/media/profile_images/")


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


@pytest.mark.django_db
def test_password_policy_public_defaults():
    client = APIClient()
    resp = client.get(reverse("password-policy-public"))
    assert resp.status_code == 200
    assert resp.data["min_length"] == settings.PASSWORD_MIN_LENGTH


@pytest.mark.django_db
def test_password_policy_update_and_fetch():
    get_user_model().objects.create_user(
        username="adm",
        password="123",
        role="platform_admin",
    )
    client = APIClient()
    login = client.post(
        reverse("login"),
        {"username": "adm", "password": "123"},
    )
    token = login.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    data = {
        "min_length": 5,
        "require_uppercase": False,
        "require_lowercase": True,
        "require_numbers": False,
        "require_symbols": False,
    }
    resp = client.put(reverse("password-policy"), data, format="json")
    assert resp.status_code == 200
    assert PasswordPolicy.objects.count() == 1
    public = client.get(reverse("password-policy-public"))
    assert public.data["min_length"] == 5


@pytest.mark.django_db
def test_login_history_and_sessions(auth_client, admin_user):
    # login already performed by auth_client fixture
    # should create history/session
    history_resp = auth_client.get(reverse("login-history"))
    assert history_resp.status_code == 200
    assert history_resp.data
    sessions_resp = auth_client.get(reverse("session-list"))
    assert sessions_resp.status_code == 200
    assert sessions_resp.data


@pytest.mark.django_db
def test_forgot_password_existing_user(monkeypatch, settings):
    user = PlatformUser.objects.create_user(
        username="sam", email="sam@example.com", password="pwd"
    )
    captured = {}

    def fake_send(email, link, name):
        captured["email"] = email
        captured["link"] = link

    monkeypatch.setattr(
        "accounts.views.send_password_reset_email", fake_send
    )

    client = APIClient()
    resp = client.post(reverse("forgot-password"), {"username": "sam"})

    assert resp.status_code == 200
    assert resp.data["success"] is True
    assert PasswordResetToken.objects.filter(user=user).count() == 1
    assert captured["email"] == "sam@example.com"
    assert captured["link"].startswith(settings.FRONTEND_URL)


@pytest.mark.django_db
def test_forgot_password_unknown_user(monkeypatch):
    called = {}

    def fake_send(*args, **kwargs):
        called["ok"] = True

    monkeypatch.setattr(
        "accounts.views.send_password_reset_email", fake_send
    )

    client = APIClient()
    resp = client.post(reverse("forgot-password"), {"username": "nope"})

    assert resp.status_code == 200
    assert resp.data["success"] is True
    assert PasswordResetToken.objects.count() == 0
    assert "ok" not in called


@pytest.mark.django_db
def test_forgot_password_missing_param():
    client = APIClient()
    resp = client.post(reverse("forgot-password"), {})
    assert resp.status_code == 400


@pytest.mark.django_db
def test_reset_password_success(monkeypatch):
    user = PlatformUser.objects.create_user(
        username="tom", email="tom@example.com", password="oldpwd"
    )
    token = PasswordResetToken.objects.create(
        user=user,
        token="abc",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    client = APIClient()
    resp = client.post(
        reverse("reset-password"),
        {"token": token.token, "password": "Newpass1!"},
    )

    assert resp.status_code == 200
    assert resp.data["success"] is True
    user.refresh_from_db()
    assert user.check_password("Newpass1!")
    assert PasswordResetToken.objects.count() == 0


@pytest.mark.django_db
def test_reset_password_invalid_token():
    client = APIClient()
    resp = client.post(
        reverse("reset-password"),
        {"token": "bad", "password": "Pwd12345"},
    )
    assert resp.status_code == 400


@pytest.mark.django_db
def test_reset_password_expired_token():
    user = PlatformUser.objects.create_user(
        username="kate", email="kate@example.com", password="oldpwd"
    )
    PasswordResetToken.objects.create(
        user=user,
        token="expired",
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    client = APIClient()
    resp = client.post(
        reverse("reset-password"),
        {"token": "expired", "password": "Pwd12345"},
    )
    assert resp.status_code == 400


@pytest.mark.django_db
def test_change_password_success():
    user = PlatformUser.objects.create_user(
        username="carlos", email="c@example.com", password="oldpass"
    )
    client = APIClient()
    login = client.post(
        reverse("login"),
        {"username": "carlos", "password": "oldpass"},
    )
    token = login.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    resp = client.post(
        reverse("change-password"),
        {"current_password": "oldpass", "new_password": "Newpass1!"},
    )

    assert resp.status_code == 200
    assert resp.data["success"] is True
    user.refresh_from_db()
    assert user.check_password("Newpass1!")


@pytest.mark.django_db
def test_change_password_wrong_current():
    user = PlatformUser.objects.create_user(
        username="eve", email="e@example.com", password="pass123"
    )
    client = APIClient()
    login = client.post(
        reverse("login"),
        {"username": "eve", "password": "pass123"},
    )
    token = login.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    resp = client.post(
        reverse("change-password"),
        {"current_password": "wrong", "new_password": "Other1!"},
    )

    assert resp.status_code == 400
    user.refresh_from_db()
    assert user.check_password("pass123")
