from django.urls import path
from .views import (
    RegisterView, LoginView, ProfileView, ChangePasswordView,
    AdminUserListView, AdminUserDetailView, AuditLogListView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("admin/users/", AdminUserListView.as_view(), name="admin_user_list"),
    path("admin/users/<uuid:pk>/", AdminUserDetailView.as_view(), name="admin_user_detail"),
    path("admin/audit-logs/", AuditLogListView.as_view(), name="audit_logs"),
]