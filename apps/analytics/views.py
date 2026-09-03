from django.db.models import Avg, Count
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assessments.models import Assessment
from apps.institutions.models import Institution


class DashboardSummaryView(APIView):
    """
    Dashboard analytics.
    
    RBAC:
    - Admin/Analyst: See ALL data
    - Assessor: See ONLY their own data
    - Viewer: See ONLY their institution's data
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Base queryset
        qs = Assessment.objects.all()
        
        # RBAC filtering
        if user.role in ("admin", "analyst"):
            pass  # See all
        elif user.role == "assessor":
            qs = qs.filter(assessor=user)
        elif user.role == "viewer":
            if user.organization:
                qs = qs.filter(institution__name=user.organization)
            else:
                qs = qs.none()
        else:
            qs = qs.none()

        submitted_qs = qs.exclude(overall_score__isnull=True)

        risk_distribution = {
            level: submitted_qs.filter(risk_level=level).count()
            for level in ["critical", "high", "medium", "low", "negligible"]
        }

        category_avgs = submitted_qs.aggregate(
            authentication=Avg("authentication_score"),
            encryption=Avg("encryption_score"),
            api_security=Avg("api_security_score"),
            data_storage=Avg("data_storage_score"),
            network_security=Avg("network_security_score"),
            incident_response=Avg("incident_response_score"),
            third_party=Avg("third_party_score"),
            compliance=Avg("compliance_score"),
        )

        compliance_avgs = submitted_qs.aggregate(
            owasp=Avg("owasp_compliance"),
            nist=Avg("nist_compliance"),
            cbn=Avg("cbn_compliance"),
        )

        # Institutions count based on role
        if user.role in ("admin", "analyst"):
            institution_count = Institution.objects.count()
            recent = qs.select_related("institution").order_by("-created_at")[:8]
        elif user.role == "assessor":
            institution_count = Institution.objects.filter(name=user.organization).count() if user.organization else 0
            recent = qs.select_related("institution").order_by("-created_at")[:8]
        elif user.role == "viewer":
            institution_count = Institution.objects.filter(name=user.organization).count() if user.organization else 0
            recent = qs.select_related("institution").order_by("-created_at")[:8]
        else:
            institution_count = 0
            recent = []

        recent_data = [
            {
                "id": str(a.id),
                "title": a.title,
                "institution": a.institution.name,
                "status": a.status,
                "overall_score": a.overall_score,
                "risk_level": a.risk_level,
                "created_at": a.created_at,
            }
            for a in recent
        ]

        return Response({
            "total_institutions": institution_count,
            "total_assessments": qs.count(),
            "completed_assessments": submitted_qs.count(),
            "average_score": round(submitted_qs.aggregate(avg=Avg("overall_score"))["avg"] or 0, 2),
            "risk_distribution": risk_distribution,
            "category_averages": {k: round(v, 2) if v else 0 for k, v in category_avgs.items()},
            "framework_compliance": {k: round(v, 2) if v else 0 for k, v in compliance_avgs.items()},
            "recent_assessments": recent_data,
            "generated_at": timezone.now(),
        })


class InstitutionAnalyticsView(APIView):
    """
    Per-institution risk trend.
    
    RBAC:
    - Admin/Analyst: Can view any institution
    - Assessor: Can view their own institution
    - Viewer: Can view their own institution
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, institution_id):
        user = request.user
        
        # RBAC: Check if user has access to this institution
        institution = Institution.objects.filter(id=institution_id).first()
        if not institution:
            return Response({"detail": "Institution not found."}, status=404)
        
        if user.role not in ("admin", "analyst"):
            if user.organization != institution.name:
                return Response({"detail": "Not permitted."}, status=403)

        assessments = Assessment.objects.filter(
            institution_id=institution_id
        ).exclude(overall_score__isnull=True).order_by("created_at")

        trend = [
            {"date": a.submitted_at or a.created_at, "overall_score": a.overall_score, "risk_level": a.risk_level}
            for a in assessments
        ]
        return Response({"institution_id": institution_id, "trend": trend})