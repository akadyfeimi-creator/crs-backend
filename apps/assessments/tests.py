from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.institutions.models import Institution
from apps.assessments.models import AssessmentQuestion, Assessment, Category, Framework

User = get_user_model()


class AssessmentFlowTests(APITestCase):
    """
    End-to-end test of Objectives 1-3 working together:
    a risk-factor question bank -> an assessment -> the scoring engine.
    """

    def setUp(self):
        self.assessor = User.objects.create_user(
            username="assessor3", email="assessor3@example.com", password="Pass123!",
            role=User.Role.ASSESSOR, organization="GTBank",
        )
        self.viewer = User.objects.create_user(
            username="viewer3", email="viewer3@example.com", password="Pass123!",
            role=User.Role.VIEWER, organization="GTBank",
        )
        self.institution = Institution.objects.create(
            name="GTBank", type=Institution.InstitutionType.BANK,
            registration_number="RC-010", email="risk@gtbank.com",
        )
        self.q1 = AssessmentQuestion.objects.create(
            category=Category.AUTHENTICATION, framework=Framework.OWASP,
            framework_reference="MASVS-AUTH-1", question_text="Is MFA enforced?", weight=1.0,
        )
        self.q2 = AssessmentQuestion.objects.create(
            category=Category.ENCRYPTION, framework=Framework.NIST,
            framework_reference="NIST-PR.DS-1", question_text="Is data encrypted at rest?", weight=1.0,
        )

    def test_question_list_requires_authentication(self):
        response = self.client.get("/api/assessments/questions/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_viewer_cannot_create_assessment(self):
        self.client.force_authenticate(self.viewer)
        response = self.client.post("/api/assessments/", {
            "title": "Q1 Review", "institution": str(self.institution.id),
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assessor_can_create_assessment_for_own_institution(self):
        self.client.force_authenticate(self.assessor)
        response = self.client.post("/api/assessments/", {
            "title": "Q1 Review", "institution": str(self.institution.id),
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_submit_assessment_with_no_responses(self):
        self.client.force_authenticate(self.assessor)
        assessment = Assessment.objects.create(
            institution=self.institution, assessor=self.assessor, title="Empty Review",
        )
        response = self.client.post(f"/api/assessments/{assessment.id}/submit/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_full_submission_computes_score_and_risk_level(self):
        """Core Objective-2/3 test: answers in -> a score and risk level out."""
        self.client.force_authenticate(self.assessor)
        assessment = Assessment.objects.create(
            institution=self.institution, assessor=self.assessor, title="Full Review",
        )
        # Answer both questions at the top maturity level (5 = Exceeds Requirements)
        save_response = self.client.post(
            f"/api/assessments/{assessment.id}/responses/",
            [
                {"question": str(self.q1.id), "score": 5, "evidence": "MFA policy doc"},
                {"question": str(self.q2.id), "score": 5, "evidence": "KMS config"},
            ],
            format="json",
        )
        self.assertEqual(save_response.status_code, status.HTTP_200_OK)

        submit_response = self.client.post(f"/api/assessments/{assessment.id}/submit/")
        self.assertEqual(submit_response.status_code, status.HTTP_200_OK)

        assessment.refresh_from_db()
        self.assertEqual(assessment.status, Assessment.Status.SUBMITTED)
        self.assertIsNotNone(assessment.overall_score)
        self.assertEqual(assessment.overall_score, 100.0)  # all max scores -> 100
        self.assertEqual(assessment.risk_level, Assessment.RiskLevel.NEGLIGIBLE)
