from django.utils import timezone
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.decorators import action

from .models import Teacher, Staff, Student, PrincipalList, PresidentList
from .serializers import (
    TeacherSerializer, StaffSerializer, StudentSerializer,
    PrincipalListSerializer, PresidentListSerializer
)

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, "role", "") == "Admin"

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all().order_by("-id")
    serializer_class = TeacherSerializer


# keep your other viewsets as-is:
class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all().order_by("-id")
    serializer_class = StaffSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all().order_by("-id")
    serializer_class = StudentSerializer

class PrincipalListViewSet(viewsets.ModelViewSet):
    queryset = PrincipalList.objects.all()
    serializer_class = PrincipalListSerializer
    ordering = ["-to_date"]

class PresidentListViewSet(viewsets.ModelViewSet):
    queryset = PresidentList.objects.all()
    serializer_class = PresidentListSerializer
    ordering = ["-to_date"]
