from rest_framework import serializers
from .models import AssessmentQuestion, Assessment, AssessmentResponse


class AssessmentQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentQuestion
        fields = ["id", "category", "framework", "framework_reference", "question_text", "description", "weight"]


class AssessmentResponseSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source="question.question_text", read_only=True)
    category = serializers.CharField(source="question.category", read_only=True)
    framework = serializers.CharField(source="question.framework", read_only=True)

    class Meta:
        model = AssessmentResponse
        fields = [
            "id", "assessment", "question", "question_text", "category",
            "framework", "score", "evidence", "notes", "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]


class AssessmentListSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source="institution.name", read_only=True)
    assessor_email = serializers.EmailField(source="assessor.email", read_only=True)

    class Meta:
        model = Assessment
        fields = [
            "id", "title", "institution", "institution_name", "assessor",
            "assessor_email", "status", "overall_score", "risk_level",
            "created_at", "submitted_at",
        ]
        read_only_fields = fields


class AssessmentDetailSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source="institution.name", read_only=True)
    responses = AssessmentResponseSerializer(many=True, read_only=True)
    assessor_email = serializers.EmailField(source="assessor.email", read_only=True)

    class Meta:
        model = Assessment
        fields = [
            "id", "title", "description", "institution", "institution_name",
            "assessor", "assessor_email", "status",
            "authentication_score", "encryption_score", "api_security_score",
            "data_storage_score", "network_security_score",
            "incident_response_score", "third_party_score", "compliance_score",
            "overall_score", "risk_level",
            "owasp_compliance", "nist_compliance", "cbn_compliance",
            "responses", "created_at", "updated_at", "submitted_at",
        ]
        read_only_fields = [
            "id", "assessor", "authentication_score", "encryption_score",
            "api_security_score", "data_storage_score", "network_security_score",
            "incident_response_score", "third_party_score", "compliance_score",
            "overall_score", "risk_level", "owasp_compliance", "nist_compliance",
            "cbn_compliance", "created_at", "updated_at", "submitted_at",
        ]


class AssessmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ["id", "title", "description", "institution"]

    def create(self, validated_data):
        validated_data["assessor"] = self.context["request"].user
        return super().create(validated_data)


class BulkResponseSerializer(serializers.Serializer):
    """Payload for saving all answers of an assessment form in one request."""
    question = serializers.UUIDField()
    score = serializers.IntegerField(min_value=0, max_value=5)
    evidence = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)