from django.urls import path
from .views import MonitoredResourceListCreateView, AlertListView

urlpatterns = [
    path("resources/", MonitoredResourceListCreateView.as_view(), name="monitoredresource-list"),
    path("alerts/", AlertListView.as_view(), name="alert-list"),
]
