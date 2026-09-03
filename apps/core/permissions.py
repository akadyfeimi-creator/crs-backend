from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Full system access — user management, all institutions, all data."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "admin")


class IsAnalystOrAdmin(BasePermission):
    """Security analysts can review/approve assessments and generate reports."""
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.role in ("admin", "analyst")
        )


class IsAssessorOrAbove(BasePermission):
    """Assessors can create and submit assessments for their institution."""
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.role in ("admin", "analyst", "assessor")
        )


class ReadOnlyOrAssessorAbove(BasePermission):
    """Viewers get read-only access; assessors and above get write access."""
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in ("admin", "analyst", "assessor")


class IsOwnerOrPrivileged(BasePermission):
    """Object-level check: owner of a record, or analyst/admin, may act on it."""
    def has_object_permission(self, request, view, obj):
        if request.user.role in ("admin", "analyst"):
            return True
        owner = getattr(obj, "assessor", None) or getattr(obj, "created_by", None) or getattr(obj, "user", None)
        return owner == request.user