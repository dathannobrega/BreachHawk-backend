from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.authentication import JWTAuthentication
from accounts.permissions import IsAdminOrPlatformAdmin
from .models import ScrapeLog, Snapshot
from .serializers import ScrapeLogSerializer, SnapshotSerializer

import os
import uuid
import importlib.util
import sys
from . import registry


class ScrapeLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ScrapeLog.objects.all()
    serializer_class = ScrapeLogSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrPlatformAdmin]


class SnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Snapshot.objects.all()
    serializer_class = SnapshotSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrPlatformAdmin]


class ScraperUploadView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrPlatformAdmin]

    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "No file provided"}, status=400)

        directory = os.path.join(os.path.dirname(__file__), "custom")
        os.makedirs(directory, exist_ok=True)

        ext = os.path.splitext(file.name)[1]
        if ext != ".py":
            return Response({"detail": "Apenas arquivos .py"}, status=400)

        filename = file.name
        if not filename.endswith(".py"):
            filename = f"{uuid.uuid4().hex}{ext}"
        path = os.path.join(directory, filename)

        with open(path, "wb+") as out_file:
            for chunk in file.chunks():
                out_file.write(chunk)

        before = set(registry.keys())
        try:
            spec = importlib.util.spec_from_file_location(filename[:-3], path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
        except Exception as exc:
            os.remove(path)
            return Response({"detail": str(exc)}, status=400)

        new_slugs = set(registry.keys()) - before
        if not new_slugs:
            os.remove(path)
            return Response({"detail": "Scraper inválido"}, status=400)
        slug = next(iter(new_slugs))
        new_path = os.path.join(directory, f"{slug}.py")
        if path != new_path:
            os.rename(path, new_path)
        return Response({"msg": "scraper uploaded", "slug": slug}, status=201)


class ScraperListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrPlatformAdmin]

    def get(self, request):
        return Response(list(registry.keys()))


class ScraperDeleteView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrPlatformAdmin]

    def delete(self, request, slug):
        directory = os.path.join(os.path.dirname(__file__), "custom")
        path = os.path.join(directory, f"{slug}.py")
        if not os.path.exists(path):
            return Response({"detail": "Scraper not found"}, status=404)
        os.remove(path)
        registry.pop(slug, None)
        return Response(status=204)
