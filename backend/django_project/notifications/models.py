from django.db import models


class SMTPConfig(models.Model):
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    from_email = models.EmailField()

    def __str__(self) -> str:  # pragma: no cover
        return f"SMTP {self.host}:{self.port}"


class Webhook(models.Model):
    user = models.ForeignKey("accounts.PlatformUser", on_delete=models.CASCADE)
    url = models.URLField()
    enabled = models.BooleanField(default=True)

    def __str__(self) -> str:  # pragma: no cover
        return self.url
