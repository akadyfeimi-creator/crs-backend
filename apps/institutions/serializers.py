from rest_framework import serializers
from .models import Institution


class InstitutionSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    assessment_count = serializers.SerializerMethodField()

    class Meta:
        model = Institution
        fields = [
            "id", "name", "type", "registration_number", "website", "email",
            "phone", "address", "platform_url", "created_by", "created_by_email",
            "assessment_count", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def get_assessment_count(self, obj):
        return obj.assessment_set.count()