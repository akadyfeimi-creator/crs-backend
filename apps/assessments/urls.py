from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import AssessmentViewSet, AssessmentQuestionListView

router = DefaultRouter()
router.register("", AssessmentViewSet, basename="assessment")

urlpatterns = [
    path("questions/", AssessmentQuestionListView.as_view(), name="question_list"),
] + router.urls