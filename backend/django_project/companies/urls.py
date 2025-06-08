from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, PlanViewSet

router = DefaultRouter()
router.register(r"companies", CompanyViewSet)
router.register(r"plans", PlanViewSet)

urlpatterns = router.urls
