from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import SiteViewSet, TelegramAccountListView

router = DefaultRouter()
router.register(r"", SiteViewSet)

urlpatterns = [
    path(
        "telegram-accounts/",
        TelegramAccountListView.as_view(),
        name="telegram-account-list",
    ),
] + router.urls
