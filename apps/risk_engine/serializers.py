from rest_framework import serializers
from .models import RiskAssessmentReport


class RiskAssessmentReportSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source="assessment.institution.name", read_only=True)
    assessment_title = serializers.CharField(source="assessment.title", read_only=True)

    class Meta:
        model = RiskAssessmentReport
        fields = [
            "id", "assessment", "assessment_title", "institution_name",
            "generated_by", "generated_at", "category_scores", "overall_score",
            "risk_level", "compliance", "critical_findings", "high_findings",
            "medium_findings", "low_findings", "recommendations",  # NEW: Include recommendations
        ]
        read_only_fields = fields