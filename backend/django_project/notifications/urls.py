from django.urls import path
from .views import SMTPConfigView, SMTPTestEmailView, UnsubscribeView

urlpatterns = [
    path("smtp/", SMTPConfigView.as_view(), name="smtp-config"),
    path("smtp/test/", SMTPTestEmailView.as_view(), name="smtp-test"),
    path("unsubscribe/", UnsubscribeView.as_view(), name="unsubscribe"),
]
