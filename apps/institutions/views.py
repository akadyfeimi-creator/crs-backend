from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.permissions import ReadOnlyOrAssessorAbove, IsAdmin, IsAnalystOrAdmin
from .models import Institution
from .serializers import InstitutionSerializer


class InstitutionViewSet(viewsets.ModelViewSet):
    """
    CRUD for institutions being assessed.
    
    RBAC:
    - Admin: Can see ALL institutions, create/edit/delete any
    - Analyst: Can see ALL institutions, create/edit
    - Assessor: Can see ONLY their own institution (by organization name)
    - Viewer: Can see ONLY their own institution (by organization name)
    """
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    permission_classes = [ReadOnlyOrAssessorAbove]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["type"]
    search_fields = ["name", "registration_number", "email"]
    ordering_fields = ["created_at", "name"]

    def get_queryset(self):
        """
        RBAC filtering:
        - Admin/Analyst: See ALL institutions
        - Assessor: See ONLY institutions where their organization matches
        - Viewer: See ONLY institutions where their organization matches
        """
        qs = super().get_queryset()
        user = self.request.user

        # Admin and Analyst can see everything
        if user.role in ("admin", "analyst"):
            return qs

        # Assessor can see only their own institution (by organization name)
        if user.role == "assessor":
            if user.organization:
                return qs.filter(name=user.organization)
            return qs.none()  # No organization assigned - see nothing

        # Viewer can see only their own institution
        if user.role == "viewer":
            if user.organization:
                return qs.filter(name=user.organization)
            return qs.none()

        # Default: see nothing
        return qs.none()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)