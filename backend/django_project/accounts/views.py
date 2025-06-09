from datetime import datetime, timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
import os
from authlib.integrations.django_client import OAuth

from .models import PlatformUser, LoginHistory, UserSession
from .serializers import (
    PlatformUserSerializer,
    LoginHistorySerializer,
    UserSessionSerializer,
)
from .authentication import JWTAuthentication

oauth = OAuth()
oauth.register(
    name="google",
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


class RegisterView(generics.CreateAPIView):
    queryset = PlatformUser.objects.all()
    serializer_class = PlatformUserSerializer

    def perform_create(self, serializer):
        password = self.request.data.get("password")
        user = serializer.save()
        if password:
            user.set_password(password)
            user.save()

        refresh = RefreshToken.for_user(user)
        self.token = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {
                "access": self.token["access"],
                "refresh": self.token["refresh"],
                "user": response.data
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username") or request.data.get("email")
        password = request.data.get("password")
        if not username or not password:
            return Response({"detail": "Missing credentials"}, status=400)
        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({"detail": "Invalid credentials"}, status=401)
        user.last_login = datetime.now(timezone.utc)
        user.save()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        LoginHistory.objects.create(
            user=user, timestamp=datetime.now(timezone.utc), success=True
        )
        UserSession.objects.create(user=user, token=access_token)
        data = PlatformUserSerializer(user).data
        return Response({
            "access": access_token,
            "refresh": str(refresh),
            "user": data
        })


class MeView(generics.RetrieveAPIView):
    serializer_class = PlatformUserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class LoginHistoryListView(generics.ListAPIView):
    serializer_class = LoginHistorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LoginHistory.objects.filter(user=self.request.user)


class SessionListView(generics.ListAPIView):
    serializer_class = UserSessionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserSession.objects.filter(user=self.request.user)


class SessionDeleteView(generics.DestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "session_id"

    def get_queryset(self):
        return UserSession.objects.filter(user=self.request.user)


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        redirect_uri = request.build_absolute_uri(reverse("google-callback"))
        return oauth.google.authorize_redirect(request, redirect_uri)


class GoogleCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = oauth.google.authorize_access_token(request)
        userinfo = token.get("userinfo")
        if not userinfo:
            return Response(
                {"detail": "Google authentication failed"},
                status=401
            )

        email = userinfo.get("email")
        first = userinfo.get("given_name")
        last = userinfo.get("family_name")
        picture = userinfo.get("picture")
        username = email.split("@")[0] if email else None

        user, created = PlatformUser.objects.get_or_create(
            email=email,
            defaults={"username": username}
        )
        updated = False
        if created:
            user.first_name = first or ""
            user.last_name = last or ""
            user.profile_image = picture
            user.set_unusable_password()
            user.save()
        else:
            if not user.first_name and first:
                user.first_name = first
                updated = True
            if not user.last_name and last:
                user.last_name = last
                updated = True
            if not user.profile_image and picture:
                user.profile_image = picture
                updated = True
            if not user.username and username:
                if not PlatformUser.objects.filter(
                    username=username
                ).exclude(id=user.id).exists():
                    user.username = username
                    updated = True
            if updated:
                user.save()

        user.last_login = datetime.now(timezone.utc)
        user.save()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        LoginHistory.objects.create(
            user=user,
            timestamp=datetime.now(timezone.utc),
            success=True
        )
        UserSession.objects.create(user=user, token=access_token)

        redirect_url = f"{settings.FRONTEND_URL}/login?token={access_token}"
        return redirect(redirect_url)
