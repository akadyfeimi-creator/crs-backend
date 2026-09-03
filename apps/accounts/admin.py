from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, AuditLog


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ["email", "username", "role", "organization", "is_verified", "is_active", "created_at"]
    list_filter = ["role", "is_active", "is_verified"]
    search_fields = ["email", "username", "organization"]
    ordering = ["-created_at"]
    fieldsets = UserAdmin.fieldsets + (
        ("Risk System Profile", {"fields": (
            "role", "organization", "phone_number", "is_verified",
            "two_factor_enabled", "last_login_ip", "failed_login_attempts", "locked_until",
        )}),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["action", "user", "ip_address", "created_at"]
    list_filter = ["action"]
    readonly_fields = [f.name for f in AuditLog._meta.fields]
    search_fields = ["action", "user__email"]