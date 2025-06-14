from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, PlanViewSet

router = DefaultRouter()
router.register(r"", CompanyViewSet, basename="company")
router.register(r"plans", PlanViewSet, basename="plan")

urlpatterns = router.urls
