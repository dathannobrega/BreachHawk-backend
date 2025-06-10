from rest_framework import serializers
from .models import PlatformUser, LoginHistory, UserSession, PasswordPolicy


class PlatformUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformUser
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "status",
            "company",
            "job_title",
            "is_subscribed",
            "profile_image",
            "organization",
            "contact",
            "failed_login_attempts",
            "lockout_until",
            "last_login",
            "date_joined",
        ]


class PlatformUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformUser
        fields = [
            "username",
            "first_name",
            "last_name",
            "company",
            "job_title",
            "is_subscribed",
            "profile_image",
            "organization",
            "contact",
        ]
        extra_kwargs = {field: {"required": False, "allow_null": True} for field in fields}


class LoginHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginHistory
        fields = [
            "id",
            "user",
            "timestamp",
            "device",
            "ip_address",
            "location",
            "success",
        ]


class UserSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSession
        fields = [
            "id",
            "user",
            "token",
            "device",
            "ip_address",
            "location",
            "created_at",
            "expires_at",
        ]


class PasswordPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordPolicy
        fields = [
            "id",
            "min_length",
            "require_uppercase",
            "require_lowercase",
            "require_numbers",
            "require_symbols",
        ]
