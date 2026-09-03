import uuid
from django.conf import settings
from django.db import models


class Institution(models.Model):
    """A mobile banking / fintech platform being assessed."""

    class InstitutionType(models.TextChoices):
        BANK = "bank", "Commercial Bank"
        FINTECH = "fintech", "Fintech Company"
        MFB = "mfbank", "Microfinance Bank"
        PSP = "payment", "Payment Service Provider"
        OTHER = "other", "Other Financial Institution"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=InstitutionType.choices, default=InstitutionType.FINTECH)
    registration_number = models.CharField(max_length=50, unique=True)
    website = models.URLField(blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    platform_url = models.URLField(blank=True, help_text="URL of the mobile banking / fintech app or platform under assessment")

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="institutions_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name