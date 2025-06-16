from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import SiteViewSet, TelegramAccountViewSet

router = DefaultRouter()
router.register(r"telegram-accounts", TelegramAccountViewSet, basename="telegram-account")
router.register(r"", SiteViewSet, basename="site")

urlpatterns = [
    path("", include(router.urls)),
]