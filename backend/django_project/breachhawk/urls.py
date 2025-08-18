"""
URL configuration for breachhawk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from .views import health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("leaks.urls")),
    path("api/accounts/", include("accounts.urls")),
    path("api/billing/", include("billing.urls")),
    path("api/companies/", include("companies.urls")),
    path("api/sites/", include("sites.urls")),
    path("api/scrapers/", include("scrapers.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/monitoring/", include("monitoring.urls")),
    path("health/", health_check),
]

# Serve static and media files during development
if settings.DEBUG:
    static_root = (
        settings.STATICFILES_DIRS[0]
        if settings.STATICFILES_DIRS
        else settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=static_root,
    )
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
