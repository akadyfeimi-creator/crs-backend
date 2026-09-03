from django.urls import path
from .views import GenerateReportView, ReportListView, ReportDetailView

urlpatterns = [
    path("assessments/<uuid:assessment_id>/generate-report/", GenerateReportView.as_view(), name="generate_report"),
    path("reports/", ReportListView.as_view(), name="report_list"),
    path("reports/<uuid:pk>/", ReportDetailView.as_view(), name="report_detail"),
]