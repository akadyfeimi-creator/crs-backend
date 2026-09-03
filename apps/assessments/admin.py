from django.contrib import admin
from .models import AssessmentQuestion, Assessment, AssessmentResponse


@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):
    list_display = ["category", "framework", "framework_reference", "weight", "is_active"]
    list_filter = ["category", "framework", "is_active"]
    search_fields = ["question_text", "framework_reference"]


class ResponseInline(admin.TabularInline):
    model = AssessmentResponse
    extra = 0
    readonly_fields = ["question", "score", "evidence"]


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ["title", "institution", "assessor", "status", "overall_score", "risk_level", "created_at"]
    list_filter = ["status", "risk_level"]
    search_fields = ["title", "institution__name"]
    inlines = [ResponseInline]


@admin.register(AssessmentResponse)
class AssessmentResponseAdmin(admin.ModelAdmin):
    list_display = ["assessment", "question", "score"]