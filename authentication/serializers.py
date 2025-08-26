# authentication/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import json

User = get_user_model()

# --------------------------
# Registration
# --------------------------
class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    full_name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "confirm_password",
            "role",
            "phone",
            "profile_picture",
            "full_name",
        )
        extra_kwargs = {
            "username": {"required": False},
            "role": {"required": False},
            "password": {"write_only": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs

    def create(self, validated):
        # pop non-model fields
        validated.pop("confirm_password", None)
        full_name = validated.pop("full_name", "").strip()

        # fallback username from email if empty
        username = validated.get("username") or validated.get("email")
        validated["username"] = username

        # optional: map full_name -> first_name/last_name on AbstractUser
        if full_name:
            first, *rest = full_name.split()
            validated["first_name"] = first
            validated["last_name"] = " ".join(rest) if rest else ""

        password = validated.pop("password")
        user = User(**validated)
        user.set_password(password)
        user.save()
        return user

# --------------------------
# Approvals
# --------------------------
class StaffApproveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "phone", "is_approved", "profile_picture"]

    def update(self, instance, validated_data):
        is_approved = validated_data.get("is_approved", instance.is_approved)
        if isinstance(is_approved, str):
            is_approved = is_approved.lower() == "true"
        instance.is_approved = is_approved
        instance.save()
        return instance

# --------------------------
# JWT
# --------------------------
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # you can add extra payload here if needed
        return data

# --------------------------
# Password change
# --------------------------
class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        user = self.context["request"].user
        if not user.is_authenticated:
            raise serializers.ValidationError({"detail": "Authentication is required to change the password."})

        if not user.check_password(data["current_password"]):
            raise serializers.ValidationError({"current_password": "Current password is incorrect."})

        if len(data["new_password"]) < 6:
            raise serializers.ValidationError({"new_password": "New password must be at least 6 characters long."})

        if data["current_password"] == data["new_password"]:
            raise serializers.ValidationError({"new_password": "New password cannot be the same as the current password."})

        return data

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()

# --------------------------
# Profiles
# --------------------------
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "profile_picture", "phone"]

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "phone", "profile_picture"]
        extra_kwargs = {
            "email": {"required": False},
            "phone": {"required": False},
            "profile_picture": {"required": False},
        }
