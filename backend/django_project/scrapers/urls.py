from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ScrapeLogViewSet,
    SnapshotViewSet,
    ScraperUploadView,
    ScraperListView,
    ScraperDeleteView,
)

router = DefaultRouter()
router.register(r"logs", ScrapeLogViewSet)
router.register(r"snapshots", SnapshotViewSet)

urlpatterns = [
    path("upload/", ScraperUploadView.as_view(), name="scraper-upload"),
    path("scrapers/", ScraperListView.as_view(), name="scraper-list"),
    path(
        "scrapers/<slug:slug>/",
        ScraperDeleteView.as_view(),
        name="scraper-delete",
    ),
] + router.urls
