from django.db import models


class Invoice(models.Model):
    stripe_id = models.CharField(max_length=255)
    customer = models.CharField(max_length=255, blank=True, null=True)
    amount_due = models.IntegerField()
    status = models.CharField(max_length=50, blank=True, null=True)
    due_date = models.IntegerField(blank=True, null=True)

    def __str__(self) -> str:  # pragma: no cover
        return self.stripe_id


class Payment(models.Model):
    stripe_id = models.CharField(max_length=255)
    amount = models.IntegerField()
    status = models.CharField(max_length=50, blank=True, null=True)
    created = models.IntegerField()

    def __str__(self) -> str:  # pragma: no cover
        return self.stripe_id


class Subscription(models.Model):
    stripe_id = models.CharField(max_length=255)
    customer = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    current_period_end = models.IntegerField(blank=True, null=True)

    def __str__(self) -> str:  # pragma: no cover
        return self.stripe_id
