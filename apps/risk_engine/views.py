from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assessments.models import Assessment
from .models import RiskAssessmentReport
from .scoring import RiskScoringEngine
from .serializers import RiskAssessmentReportSerializer


class GenerateReportView(APIView):
    """
    Generate a risk assessment report with recommendations.
    
    RBAC:
    - Admin/Analyst: Can generate for any assessment
    - Assessor: Can generate for their own assessments
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, assessment_id):
        user = request.user
        
        try:
            assessment = Assessment.objects.prefetch_related("responses__question").get(id=assessment_id)
        except Assessment.DoesNotExist:
            return Response({"detail": "Assessment not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # RBAC: Only the assessor who owns it or admin/analyst can generate report
        if assessment.assessor != user and user.role not in ("admin", "analyst"):
            return Response({"detail": "Not permitted."}, status=status.HTTP_403_FORBIDDEN)

        responses = list(assessment.responses.select_related("question").all())
        if not responses:
            return Response({"detail": "Assessment has no responses to score."}, status=400)

        engine = RiskScoringEngine()
        result = engine.score_assessment(assessment, responses)
        assessment.save()

        report = RiskAssessmentReport.objects.create(
            assessment=assessment,
            generated_by=user,
            category_scores=result["category_scores"],
            overall_score=result["overall_score"],
            risk_level=result["risk_level"]["level"],
            compliance=result["compliance"],
            critical_findings=result["findings"]["critical"],
            high_findings=result["findings"]["high"],
            medium_findings=result["findings"]["medium"],
            low_findings=result["findings"]["low"],
            recommendations=result["recommendations"],  # NEW: Save recommendations
        )
        return Response(RiskAssessmentReportSerializer(report).data, status=status.HTTP_201_CREATED)


class ReportListView(generics.ListAPIView):
    """
    List reports.
    
    RBAC:
    - Admin/Analyst: See ALL reports
    - Assessor: See ONLY their own reports
    - Viewer: See ONLY their institution's reports
    """
    serializer_class = RiskAssessmentReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # Return all reports

    def get_queryset(self):
        qs = RiskAssessmentReport.objects.select_related("assessment", "assessment__institution")
        user = self.request.user

        if user.role in ("admin", "analyst"):
            return qs

        if user.role == "assessor":
            return qs.filter(assessment__assessor=user)

        if user.role == "viewer":
            if user.organization:
                return qs.filter(assessment__institution__name=user.organization)
            return qs.none()

        return qs.none()


class ReportDetailView(generics.RetrieveAPIView):
    """
    Get report detail with recommendations.
    
    RBAC:
    - Admin/Analyst: Can view any report
    - Assessor: Can view their own reports
    - Viewer: Can view their institution's reports
    """
    queryset = RiskAssessmentReport.objects.select_related("assessment", "assessment__institution")
    serializer_class = RiskAssessmentReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if user.role in ("admin", "analyst"):
            return qs

        if user.role == "assessor":
            return qs.filter(assessment__assessor=user)

        if user.role == "viewer":
            if user.organization:
                return qs.filter(assessment__institution__name=user.organization)
            return qs.none()

        return qs.none()