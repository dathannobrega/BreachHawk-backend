from django.urls import path
from .views import SMTPConfigView, SMTPTestEmailView

urlpatterns = [
    path("smtp/", SMTPConfigView.as_view(), name="smtp-config"),
    path("smtp/test/", SMTPTestEmailView.as_view(), name="smtp-test"),
]
