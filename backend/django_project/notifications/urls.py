from django.urls import path
from .views import SMTPConfigView

urlpatterns = [
    path("smtp/", SMTPConfigView.as_view(), name="smtp-config"),
]
