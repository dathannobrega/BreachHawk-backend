from django.urls import path
from .views import LeakListCreateView, LeakSearchView

urlpatterns = [
    path("leaks/", LeakListCreateView.as_view(), name="leak-list"),
    path("leaks/search/", LeakSearchView.as_view(), name="leak-search"),
]
