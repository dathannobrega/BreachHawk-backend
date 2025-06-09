from django.db import models


class Plan(models.Model):
    class Scope(models.TextChoices):
        USER = "user", "User"
        COMPANY = "company", "Company"

    name = models.CharField(max_length=255, unique=True)
    scope = models.CharField(max_length=20, choices=Scope.choices)
    max_monitored_items = models.IntegerField()
    max_users = models.IntegerField(blank=True, null=True)
    max_searches = models.IntegerField(blank=True, null=True)

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class Company(models.Model):
    class PlanType(models.TextChoices):
        TRIAL = "trial", "Trial"
        BASIC = "basic", "Basic"
        PROFESSIONAL = "professional", "Professional"
        ENTERPRISE = "enterprise", "Enterprise"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        SUSPENDED = "suspended", "Suspended"

    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True)
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    plan = models.CharField(
        max_length=20, choices=PlanType.choices, default=PlanType.TRIAL
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    monthly_revenue = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover
        return self.name
