from django.contrib.auth import get_user_model
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.core.permissions import IsAdmin
from .models import AuditLog
from .serializers import (
    RegisterSerializer, UserSerializer, AdminUserSerializer,
    ChangePasswordSerializer, CustomTokenObtainPairSerializer,
)

User = get_user_model()


def _client_ip(request):
    """
    Get the real client IP address.
    Handles proxies (Render/Cloudflare) that send comma-separated IPs.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if x_forwarded_for:
        # Get the FIRST IP from the comma-separated list
        ip = x_forwarded_for.split(",")[0].strip()
        return ip
    return request.META.get("REMOTE_ADDR", "unknown")


def log_action(user, action, request, **details):
    AuditLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        action=action,
        ip_address=_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        details=details,
    )


class RegisterView(generics.CreateAPIView):
    """Public self-registration — always created as 'viewer' role."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        log_action(None, "user_registered", request, email=request.data.get("email"))
        return response


@method_decorator(ratelimit(key="ip", rate="5/m", method="POST", block=True), name="post")
class LoginView(TokenObtainPairView):
    """
    JWT login, rate-limited to mitigate credential-stuffing / brute force.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            try:
                user = User.objects.get(email=request.data.get("email"))
                # FIX: Use _client_ip() which handles proxy IPs
                user.last_login_ip = _client_ip(request)
                user.failed_login_attempts = 0
                user.save(update_fields=["last_login_ip", "failed_login_attempts"])
                log_action(user, "login_success", request)
            except User.DoesNotExist:
                pass
        else:
            log_action(None, "login_failed", request, email=request.data.get("email"))
        return response


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"old_password": "Incorrect password."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        log_action(user, "password_changed", request)
        return Response({"detail": "Password updated successfully."})


class AdminUserListView(APIView):
    """
    Admin-only: list all users (User Management screen).
    Supports pagination - 10 users per page.
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))
        
        all_users = User.objects.all().order_by("-created_at")
        
        total_count = all_users.count()
        total_pages = (total_count + page_size - 1) // page_size
        
        if page < 1:
            page = 1
        if page > total_pages and total_pages > 0:
            page = total_pages
        
        start = (page - 1) * page_size
        end = start + page_size
        users = all_users[start:end]
        
        data = {
            "count": total_count,
            "next": page + 1 if page < total_pages else None,
            "previous": page - 1 if page > 1 else None,
            "results": [
                {
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "organization": user.organization,
                    "role": user.role,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                    "failed_login_attempts": user.failed_login_attempts,
                    "locked_until": user.locked_until,
                    "created_at": user.created_at,
                }
                for user in users
            ],
        }
        
        return Response(data)


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin-only: view/update/deactivate a user, including role changes."""
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, "user_updated_by_admin", self.request, target=str(instance.id))


class AuditLogListView(APIView):
    """
    Admin/analyst-only: view the system audit trail.
    Supports pagination - 10 logs per page.
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))
        
        all_logs = AuditLog.objects.select_related("user").all().order_by("-created_at")
        
        total_count = all_logs.count()
        total_pages = (total_count + page_size - 1) // page_size
        
        if page < 1:
            page = 1
        if page > total_pages and total_pages > 0:
            page = total_pages
        
        start = (page - 1) * page_size
        end = start + page_size
        logs = all_logs[start:end]
        
        data = {
            "count": total_count,
            "next": page + 1 if page < total_pages else None,
            "previous": page - 1 if page > 1 else None,
            "results": [
                {
                    "id": str(log.id),
                    "user": log.user.email if log.user else "anonymous",
                    "action": log.action,
                    "ip_address": log.ip_address,
                    "details": log.details,
                    "created_at": log.created_at,
                }
                for log in logs
            ],
        }
        
        return Response(data)