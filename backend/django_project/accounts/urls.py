from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    MeView,
    ProfileImageUploadView,
    LoginHistoryListView,
    SessionListView,
    SessionDeleteView,
    GoogleLoginView,
    GoogleCallbackView,
    PasswordPolicyView,
    PasswordPolicyPublicView,
    PlatformUserViewSet,
    UserLoginHistoryView,
    UserSessionListView,
)

router = DefaultRouter()
router.register(r"platform-users", PlatformUserViewSet, basename="platformuser")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="me"),
    path(
        "me/profile-image/",
        ProfileImageUploadView.as_view(),
        name="profile-image",
    ),
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
    path(
        "platform-users/<int:user_id>/login-history/",
        UserLoginHistoryView.as_view(),
        name="platform-user-login-history",
    ),
    path(
        "platform-users/<int:user_id>/sessions/",
        UserSessionListView.as_view(),
        name="platform-user-session-list",
    ),
]

urlpatterns += router.urls
