from django.db import models
from django.utils import timezone


class Site(models.Model):
    class AuthType(models.TextChoices):
        NONE = "none", "None"
        BASIC = "basic", "Basic"
        FORM = "form", "Form"

    class CaptchaType(models.TextChoices):
        NONE = "none", "None"
        IMAGE = "image", "Image"
        MATH = "math", "Math"
        ROTATED = "rotated", "Rotated"

    class SiteType(models.TextChoices):
        FORUM = "forum", "Forum"
        WEBSITE = "website", "Website"
        TELEGRAM = "telegram", "Telegram"
        DISCORD = "discord", "Discord"
        PASTE = "paste", "Paste"

    name = models.CharField(max_length=255)
    url = models.URLField(unique=True, blank=True, null=True)
    type = models.CharField(
        max_length=20, choices=SiteType.choices, default=SiteType.WEBSITE
    )
    auth_type = models.CharField(
        max_length=20, choices=AuthType.choices, default=AuthType.NONE
    )
    captcha_type = models.CharField(
        max_length=20, choices=CaptchaType.choices, default=CaptchaType.NONE
    )
    scraper = models.CharField(max_length=255, default="generic")
    needs_js = models.BooleanField(default=False)
    frequency_minutes = models.PositiveIntegerField(default=60)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    bypass_config = models.JSONField(blank=True, null=True)
    credentials = models.JSONField(blank=True, null=True)
    telegram_account = models.ForeignKey(
        "TelegramAccount", on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class SiteLink(models.Model):
    site = models.ForeignKey(
        Site, related_name="links", on_delete=models.CASCADE
    )
    url = models.URLField(unique=True, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("site", "url")

    def __str__(self) -> str:  # pragma: no cover
        return self.url


class SiteMetrics(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    retries = models.IntegerField(default=0)
    permanent_fail = models.BooleanField(default=False)


class TelegramAccount(models.Model):
    api_id = models.IntegerField()
    api_hash = models.CharField(max_length=255)
    session_string = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"Account {self.id}"
