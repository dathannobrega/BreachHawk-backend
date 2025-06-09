from django.db import models


class Leak(models.Model):
    site = models.ForeignKey(
        "sites.Site", on_delete=models.CASCADE, null=True, blank=True
    )
    company = models.CharField(max_length=255)
    country = models.CharField(max_length=255, blank=True, null=True)
    found_at = models.DateTimeField(auto_now_add=True)
    source_url = models.URLField()
    views = models.IntegerField(blank=True, null=True)
    publication_date = models.DateTimeField(blank=True, null=True)
    amount_of_data = models.CharField(max_length=255, blank=True, null=True)
    information = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    download_links = models.JSONField(blank=True, null=True)
    rar_password = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ("company", "source_url")
        ordering = ["-found_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.company} - {self.source_url}"
