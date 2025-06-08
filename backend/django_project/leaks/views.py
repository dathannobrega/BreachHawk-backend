from rest_framework import generics
from .models import Leak
from .serializers import LeakSerializer


class LeakListCreateView(generics.ListCreateAPIView):
    queryset = Leak.objects.all()
    serializer_class = LeakSerializer
