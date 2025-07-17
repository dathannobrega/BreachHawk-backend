from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.authentication import JWTAuthentication
from accounts.models import UserSearchQuota
from .models import Leak
from .serializers import LeakSerializer
from .mongo_utils import search_leaks


class LeakListCreateView(generics.ListCreateAPIView):
    queryset = Leak.objects.all()
    serializer_class = LeakSerializer


class LeakSearchView(APIView):
    """Search leaks in MongoDB and decrement user quota."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        query = request.query_params.get("q")
        if not query:
            return Response({"detail": "Missing query"}, status=400)

        quota, _ = UserSearchQuota.objects.get_or_create(user=request.user)
        if quota.remaining <= 0:
            return Response({"detail": "Search quota exceeded"}, status=403)

        docs = search_leaks(query)
        quota.remaining -= 1
        quota.save(update_fields=["remaining", "updated_at"])
        data = [doc.model_dump(mode="json") for doc in docs]
        return Response({"results": data}, status=status.HTTP_200_OK)
