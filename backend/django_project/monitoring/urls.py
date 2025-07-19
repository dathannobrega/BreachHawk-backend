from django.urls import path

from .views import (
    AlertAckView,
    AlertListView,
    MonitoredResourceDetailView,
    MonitoredResourceListCreateView,
)

urlpatterns = [
    path(
        "resources/",
        MonitoredResourceListCreateView.as_view(),
        name="monitoredresource-list",
    ),
    path(
        "resources/<int:pk>/",
        MonitoredResourceDetailView.as_view(),
        name="monitoredresource-detail",
    ),
    path("alerts/", AlertListView.as_view(), name="alert-list"),
    path(
        "alerts/<int:pk>/ack/",
        AlertAckView.as_view(),
        name="alert-ack",
    ),
]
