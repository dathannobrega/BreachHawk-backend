from django.db import models


class MonitoredResource(models.Model):
    user = models.ForeignKey(
        "accounts.PlatformUser", on_delete=models.CASCADE
    )
    keyword = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user} - {self.keyword}"


class Alert(models.Model):
    user = models.ForeignKey(
        "accounts.PlatformUser", on_delete=models.CASCADE
    )
    resource = models.ForeignKey(
        MonitoredResource, on_delete=models.CASCADE
    )
    leak = models.ForeignKey("leaks.Leak", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "resource", "leak")
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"Alert {self.resource.keyword} -> {self.leak.id}"
