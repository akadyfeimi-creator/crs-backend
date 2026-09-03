import uuid
from django.conf import settings
from django.db import models

from apps.assessments.models import Assessment


class RiskAssessmentReport(models.Model):
    """
    Persisted snapshot of a scoring run.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="reports")
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    category_scores = models.JSONField(default=dict)
    overall_score = models.FloatField(default=0)
    risk_level = models.CharField(max_length=20, default="medium")
    compliance = models.JSONField(default=dict)

    critical_findings = models.JSONField(default=list)
    high_findings = models.JSONField(default=list)
    medium_findings = models.JSONField(default=list)
    low_findings = models.JSONField(default=list)
    
    # NEW: Add recommendations field
    recommendations = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-generated_at"]

    def __str__(self):
        return f"Report for {self.assessment.title} ({self.risk_level})"


class SecurityTrend(models.Model):
    """Pre-aggregated monthly stats to keep the dashboard fast."""
    period = models.DateField(unique=True)
    total_assessments = models.IntegerField(default=0)
    average_score = models.FloatField(default=0)
    critical_count = models.IntegerField(default=0)
    high_count = models.IntegerField(default=0)
    medium_count = models.IntegerField(default=0)
    low_count = models.IntegerField(default=0)
    negligible_count = models.IntegerField(default=0)

    class Meta:
        ordering = ["period"]