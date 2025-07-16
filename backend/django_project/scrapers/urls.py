from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ScrapeLogViewSet,
    SnapshotViewSet,
    ScraperUploadView,
    ScraperListView,
    ScraperDeleteView,
    RunScraperView,
    TaskStatusView,
    SiteLogListView,
)

router = DefaultRouter()
router.register(r"logs", ScrapeLogViewSet)
router.register(r"snapshots", SnapshotViewSet)

urlpatterns = [
    path("upload/", ScraperUploadView.as_view(), name="scraper-upload"),
    path(
        "sites/<int:site_id>/run/",
        RunScraperView.as_view(),
        name="scraper-run",
    ),
    path(
        "tasks/<uuid:task_id>/",
        TaskStatusView.as_view(),
        name="scraper-task-status",
    ),
    path(
        "sites/<int:site_id>/logs/",
        SiteLogListView.as_view(),
        name="site-log-list",
    ),
    path("scrapers/", ScraperListView.as_view(), name="scraper-list"),
    path(
        "scrapers/<slug:slug>/",
        ScraperDeleteView.as_view(),
        name="scraper-delete",
    ),
] + router.urls
