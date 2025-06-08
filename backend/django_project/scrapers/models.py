from django.db import models


class ScrapeLog(models.Model):
    site = models.ForeignKey("sites.Site", on_delete=models.CASCADE)
    url = models.URLField()
    success = models.BooleanField()
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.site} - {self.url}"


class Snapshot(models.Model):
    site = models.ForeignKey("sites.Site", on_delete=models.CASCADE)
    taken_at = models.DateTimeField(auto_now_add=True)
    screenshot = models.BinaryField(default=bytes)
    html = models.TextField(blank=True, null=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"Snapshot {self.id} for {self.site}"
