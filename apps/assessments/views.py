from django.utils import timezone
from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.permissions import ReadOnlyOrAssessorAbove, IsOwnerOrPrivileged
from apps.risk_engine.scoring import RiskScoringEngine
from .models import AssessmentQuestion, Assessment, AssessmentResponse
from .serializers import (
    AssessmentQuestionSerializer, AssessmentListSerializer,
    AssessmentDetailSerializer, AssessmentCreateSerializer,
    AssessmentResponseSerializer, BulkResponseSerializer,
)


class AssessmentQuestionListView(generics.ListAPIView):
    """Read-only question bank — used to render the assessment form."""
    queryset = AssessmentQuestion.objects.filter(is_active=True)
    serializer_class = AssessmentQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category", "framework"]
    pagination_class = None  # Return all questions at once


class AssessmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Assessments.
    
    RBAC:
    - Admin/Analyst: Can see ALL assessments, create/edit any
    - Assessor: Can see ONLY their own assessments, create/edit their own
    - Viewer: Can see ONLY their institution's assessments, read-only
    """
    queryset = Assessment.objects.select_related("institution", "assessor").prefetch_related("responses__question")
    permission_classes = [ReadOnlyOrAssessorAbove, IsOwnerOrPrivileged]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "risk_level", "institution"]

    def get_serializer_class(self):
        if self.action == "list":
            return AssessmentListSerializer
        if self.action == "create":
            return AssessmentCreateSerializer
        return AssessmentDetailSerializer

    def get_queryset(self):
        """
        RBAC filtering:
        - Admin/Analyst: See ALL assessments
        - Assessor: See ONLY their own assessments
        - Viewer: See ONLY assessments for their institution
        """
        qs = super().get_queryset()
        user = self.request.user

        # Admin and Analyst can see everything
        if user.role in ("admin", "analyst"):
            return qs

        # Assessor can see only their own assessments
        if user.role == "assessor":
            return qs.filter(assessor=user)

        # Viewer can see assessments for their institution
        if user.role == "viewer":
            if user.organization:
                return qs.filter(institution__name=user.organization)
            return qs.none()

        # Default: see nothing
        return qs.none()

    def create(self, request, *args, **kwargs):
        """Create assessment - only assessors, analysts, admins can create"""
        user = request.user
        if user.role not in ("assessor", "analyst", "admin"):
            return Response(
                {"detail": "You do not have permission to create assessments."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Assessor can only create for their own institution
        if user.role == "assessor":
            if user.organization:
                institution = serializer.validated_data.get("institution")
                if institution.name != user.organization:
                    return Response(
                        {"detail": "You can only create assessments for your own institution."},
                        status=status.HTTP_403_FORBIDDEN
                    )
        
        serializer.save(assessor=user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=["post"], url_path="responses")
    def save_responses(self, request, pk=None):
        """Save assessment responses - only the assessor who owns it"""
        assessment = self.get_object()
        user = request.user
        
        # Only the assessor who owns it or admin/analyst can modify
        if assessment.assessor != user and user.role not in ("admin", "analyst"):
            return Response(
                {"detail": "You do not have permission to modify this assessment."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = BulkResponseSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        for item in serializer.validated_data:
            AssessmentResponse.objects.update_or_create(
                assessment=assessment,
                question_id=item["question"],
                defaults={
                    "score": item["score"],
                    "evidence": item.get("evidence", ""),
                    "notes": item.get("notes", ""),
                },
            )
        
        if assessment.status == Assessment.Status.DRAFT:
            assessment.status = Assessment.Status.IN_PROGRESS
            assessment.save(update_fields=["status"])

        responses = assessment.responses.select_related("question").all()
        return Response(
            AssessmentResponseSerializer(responses, many=True).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], url_path="submit")
    def submit(self, request, pk=None):
        """Submit assessment for scoring - only the assessor who owns it"""
        assessment = self.get_object()
        user = request.user
        
        # Only the assessor who owns it or admin/analyst can submit
        if assessment.assessor != user and user.role not in ("admin", "analyst"):
            return Response(
                {"detail": "You do not have permission to submit this assessment."},
                status=status.HTTP_403_FORBIDDEN
            )

        responses = list(assessment.responses.select_related("question").all())
        
        if not responses:
            return Response(
                {"detail": "Cannot submit an assessment with no responses."},
                status=status.HTTP_400_BAD_REQUEST
            )

        engine = RiskScoringEngine()
        result = engine.score_assessment(assessment, responses)
        
        assessment.status = Assessment.Status.SUBMITTED
        assessment.submitted_at = timezone.now()
        assessment.save()

        return Response(
            {
                "assessment": AssessmentDetailSerializer(assessment).data,
                "scoring_result": result,
            },
            status=status.HTTP_200_OK
        )