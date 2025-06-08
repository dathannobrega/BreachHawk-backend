from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from accounts.authentication import JWTAuthentication
from .models import Company, Plan
from .serializers import CompanySerializer, PlanSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]


class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
