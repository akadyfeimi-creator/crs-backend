from django.urls import path
from .views import DashboardSummaryView, InstitutionAnalyticsView

urlpatterns = [
    path("dashboard/", DashboardSummaryView.as_view(), name="dashboard_summary"),
    path("institutions/<uuid:institution_id>/", InstitutionAnalyticsView.as_view(), name="institution_analytics"),
]