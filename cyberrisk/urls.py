from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Cybersecurity Risk Assessment System API",
        default_version="v1",
        description="MSc Project — Risk assessment of Nigerian mobile banking & fintech platforms",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/institutions/", include("apps.institutions.urls")),
    path("api/assessments/", include("apps.assessments.urls")),
    path("api/risk/", include("apps.risk_engine.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
    path("api/docs/", schema_view.with_ui("swagger", cache_timeout=0), name="api-docs"),
]