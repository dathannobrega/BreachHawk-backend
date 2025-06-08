from datetime import datetime, timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import PlatformUser, LoginHistory, UserSession
from .serializers import PlatformUserSerializer, LoginHistorySerializer, UserSessionSerializer
from .authentication import JWTAuthentication


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
            {"access": self.token["access"], "refresh": self.token["refresh"], "user": response.data},
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
        LoginHistory.objects.create(user=user, timestamp=datetime.now(timezone.utc), success=True)
        UserSession.objects.create(user=user, token=access_token)
        data = PlatformUserSerializer(user).data
        return Response({"access": access_token, "refresh": str(refresh), "user": data})


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
