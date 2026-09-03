import uuid
from django.conf import settings
from django.db import models

from apps.institutions.models import Institution


class Category(models.TextChoices):
    AUTHENTICATION = "authentication", "Authentication & Authorization"
    ENCRYPTION = "encryption", "Encryption & Data Protection"
    API_SECURITY = "api_security", "API Security"
    DATA_STORAGE = "data_storage", "Data Storage & Privacy"
    NETWORK_SECURITY = "network_security", "Network Security"
    INCIDENT_RESPONSE = "incident_response", "Incident Response"
    THIRD_PARTY = "third_party", "Third-Party Risk"
    COMPLIANCE = "compliance", "Compliance & Regulatory"


class Framework(models.TextChoices):
    OWASP = "owasp", "OWASP MASVS"
    NIST = "nist", "NIST Cybersecurity Framework"
    CBN = "cbn", "CBN Risk-Based Cybersecurity Framework"


class AssessmentQuestion(models.Model):
    """
    A single risk-factor control question. This is the operationalisation
    of Objective 1 (identify risk factors) and Objective 2 (design the
    risk scoring framework linking risk factors to security frameworks).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(max_length=50, choices=Category.choices)
    framework = models.CharField(max_length=20, choices=Framework.choices)
    framework_reference = models.CharField(max_length=100, blank=True)
    question_text = models.TextField()
    description = models.TextField(blank=True)
    weight = models.FloatField(default=1.0, help_text="Relative importance of this control within its category")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "framework"]

    def __str__(self):
        return f"[{self.framework}] {self.question_text[:60]}"


class Assessment(models.Model):
    """One risk assessment run against an institution's platform."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        IN_PROGRESS = "in_progress", "In Progress"
        SUBMITTED = "submitted", "Submitted"
        REVIEWED = "reviewed", "Reviewed"
        COMPLETED = "completed", "Completed"

    class RiskLevel(models.TextChoices):
        CRITICAL = "critical", "Critical"
        HIGH = "high", "High"
        MEDIUM = "medium", "Medium"
        LOW = "low", "Low"
        NEGLIGIBLE = "negligible", "Negligible"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="assessment_set")
    assessor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assessments")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    # per-category scores (0-100), computed by the risk scoring engine
    authentication_score = models.FloatField(null=True, blank=True)
    encryption_score = models.FloatField(null=True, blank=True)
    api_security_score = models.FloatField(null=True, blank=True)
    data_storage_score = models.FloatField(null=True, blank=True)
    network_security_score = models.FloatField(null=True, blank=True)
    incident_response_score = models.FloatField(null=True, blank=True)
    third_party_score = models.FloatField(null=True, blank=True)
    compliance_score = models.FloatField(null=True, blank=True)

    overall_score = models.FloatField(null=True, blank=True)
    risk_level = models.CharField(max_length=20, choices=RiskLevel.choices, null=True, blank=True)

    owasp_compliance = models.FloatField(null=True, blank=True)
    nist_compliance = models.FloatField(null=True, blank=True)
    cbn_compliance = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} — {self.institution.name}"

    def category_score_map(self):
        return {
            Category.AUTHENTICATION: self.authentication_score,
            Category.ENCRYPTION: self.encryption_score,
            Category.API_SECURITY: self.api_security_score,
            Category.DATA_STORAGE: self.data_storage_score,
            Category.NETWORK_SECURITY: self.network_security_score,
            Category.INCIDENT_RESPONSE: self.incident_response_score,
            Category.THIRD_PARTY: self.third_party_score,
            Category.COMPLIANCE: self.compliance_score,
        }


class AssessmentResponse(models.Model):
    """The assessor's answer (0-5 maturity scale) to a single control question."""

    class Score(models.IntegerChoices):
        NOT_IMPLEMENTED = 0, "Not Implemented"
        PARTIALLY_IMPLEMENTED = 1, "Partially Implemented"
        IMPLEMENTED_WEAK = 2, "Implemented but Weak"
        IMPLEMENTED_EFFECTIVE = 3, "Implemented and Effective"
        IMPLEMENTED_AUDITED = 4, "Implemented and Audited"
        EXCEEDS = 5, "Exceeds Requirements"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="responses")
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE, related_name="responses")
    score = models.IntegerField(choices=Score.choices, default=Score.NOT_IMPLEMENTED)
    evidence = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["assessment", "question"]

    def __str__(self):
        return f"{self.assessment_id} / {self.question_id} = {self.score}"