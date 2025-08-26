from rest_framework import serializers
from .models import Teacher, Staff, Student, PrincipalList, PresidentList
from institution.utils.image_compressor import compress_image


# ---------- Utility Mixin for image compression ----------
class _CompressImageMixin:
    image_field_names = ("photo",)

    def _compress_incoming_images(self, validated_data):
        for field in self.image_field_names:
            if field in validated_data and validated_data[field]:
                validated_data[field] = compress_image(validated_data[field], max_size_kb=200)
        return validated_data

    def create(self, validated_data):
        validated_data = self._compress_incoming_images(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self._compress_incoming_images(validated_data)
        return super().update(instance, validated_data)


# ---------- Teacher ----------
class TeacherSerializer(_CompressImageMixin, serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = "__all__"


# ---------- Staff ----------
class StaffSerializer(_CompressImageMixin, serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = "__all__"


# ---------- Student ----------
class StudentSerializer(_CompressImageMixin, serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"


# ---------- Principal List ----------
class PrincipalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrincipalList
        fields = "__all__"


# ---------- President List ----------
class PresidentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PresidentList
        fields = "__all__"
