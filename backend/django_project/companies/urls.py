from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, PlanViewSet

app_name = 'companies'

# Create routers for companies and plans
company_router = DefaultRouter()
company_router.register(r'', CompanyViewSet, basename='company')

plan_router = DefaultRouter()
plan_router.register(r'', PlanViewSet, basename='plan')

# Define URL patterns with explicit paths
urlpatterns = [
    # Company URLs at the root level
    path('', include(company_router.urls)),

    # Plan URLs with explicit 'plans/' prefix
    path('plans/', include(plan_router.urls)),
]
