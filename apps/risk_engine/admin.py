from django.contrib import admin
from .models import RiskAssessmentReport, SecurityTrend


@admin.register(RiskAssessmentReport)
class RiskAssessmentReportAdmin(admin.ModelAdmin):
    list_display = ["assessment", "overall_score", "risk_level", "generated_at"]
    list_filter = ["risk_level"]


@admin.register(SecurityTrend)
class SecurityTrendAdmin(admin.ModelAdmin):
    list_display = ["period", "total_assessments", "average_score"]