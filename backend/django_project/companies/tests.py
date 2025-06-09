import pytest
from .models import Company, Plan


@pytest.mark.django_db
def test_create_company_and_plan():
    # Create plan object (used to verify count later)
    Plan.objects.create(
        name="Basic",
        scope=Plan.Scope.USER,
        max_monitored_items=10,
    )
    company = Company.objects.create(
        name="Acme",
        domain="acme.com",
        plan=Company.PlanType.BASIC,
    )
    assert company.plan == Company.PlanType.BASIC
    assert Company.objects.count() == 1
    assert Plan.objects.count() == 1
