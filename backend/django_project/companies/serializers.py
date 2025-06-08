from rest_framework import serializers
from .models import Company, Plan


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            "id",
            "name",
            "scope",
            "max_monitored_items",
            "max_users",
            "max_searches",
        ]


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "domain",
            "contact_name",
            "contact_email",
            "plan",
            "status",
            "monthly_revenue",
            "created_at",
        ]
