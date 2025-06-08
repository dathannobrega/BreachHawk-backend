from rest_framework.routers import DefaultRouter
from .views import ScrapeLogViewSet, SnapshotViewSet

router = DefaultRouter()
router.register(r"logs", ScrapeLogViewSet)
router.register(r"snapshots", SnapshotViewSet)

urlpatterns = router.urls
