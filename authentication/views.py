from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListCreateAPIView
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser  # <-- add parsers

User = get_user_model()

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, "role", None) == "Admin"


class UserRegistrationView(ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]  # <-- accept JSON + multipart + form-data

    def create(self, request, *args, **kwargs):
        # print("Received data:", request.data)  # optional debug
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)   # this was already here
        self.perform_create(serializer)
        return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)


class StaffListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = StaffApproveSerializer


class StaffApproveView(generics.RetrieveUpdateDestroyAPIView):  # GET, PUT, DELETE
    permission_classes = [IsAdmin]
    queryset = User.objects.all()
    serializer_class = StaffApproveSerializer

    def update(self, request, *args, **kwargs):
        user = self.get_object()

        is_approved = request.data.get("is_approved")
        if isinstance(is_approved, str):
            is_approved = is_approved.lower() == "true"

        try:
            user.is_approved = is_approved
            user.role = "Teacher"
            user.save()
            return Response(
                {"message": f"User {user.username} approval status updated successfully."},
                status=status.HTTP_200_OK,
            )
        except IntegrityError:
            return Response(
                {"error": "Database integrity error. Check related data."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response(
            {"message": f"User {user.username} deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_authenticated:
            serializer = UserProfileSerializer(request.user)
            return Response(serializer.data)
        else:
            return Response({"error": "User not authenticated"}, status=401)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication is required."}, status=401)

        serializer = PasswordChangeSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Password updated successfully."})

        # print("Validation errors:", serializer.errors)
        return Response(serializer.errors, status=400)


class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully", "data": serializer.data}, status=200)
        return Response(serializer.errors, status=400)
