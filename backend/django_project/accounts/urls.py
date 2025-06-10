from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    MeView,
    LoginHistoryListView,
    SessionListView,
    SessionDeleteView,
    GoogleLoginView,
    GoogleCallbackView,
    PasswordPolicyView,
    PasswordPolicyPublicView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="me"),
    path(
        "login-history/",
        LoginHistoryListView.as_view(),
        name="login-history",
    ),
    path("sessions/", SessionListView.as_view(), name="session-list"),
    path(
        "sessions/<int:session_id>/",
        SessionDeleteView.as_view(),
        name="session-delete"
    ),
    path(
        "login/google/",
        GoogleLoginView.as_view(),
        name="google-login"
    ),
    path(
        "callback/google/",
        GoogleCallbackView.as_view(),
        name="google-callback"
    ),
    path(
        "password-policy/",
        PasswordPolicyView.as_view(),
        name="password-policy",
    ),
    path(
        "password-policy/public/",
        PasswordPolicyPublicView.as_view(),
        name="password-policy-public",
    ),
]
