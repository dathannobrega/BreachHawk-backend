from django.urls import path
from .views import LeakListCreateView

urlpatterns = [
    path("leaks/", LeakListCreateView.as_view(), name="leak-list"),
]
