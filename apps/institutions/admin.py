from django.contrib import admin
from .models import Institution


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ["name", "type", "registration_number", "created_by", "created_at"]
    list_filter = ["type"]
    search_fields = ["name", "registration_number"]