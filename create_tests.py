import os

# Ensure directories exist
os.makedirs("apps/accounts", exist_ok=True)
os.makedirs("apps/institutions", exist_ok=True)
os.makedirs("apps/assessments", exist_ok=True)
os.makedirs("apps/risk_engine", exist_ok=True)

# Create __init__.py files
for app in ["", "accounts", "institutions", "assessments", "risk_engine", "analytics", "core"]:
    path = f"apps/{app}/__init__.py" if app else "apps/__init__.py"
    with open(path, "w") as f:
        f.write("")

# ============================================================
# ACCOUNTS TESTS
# ============================================================
accounts_tests = '''import uuid
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class RegistrationTests(APITestCase):
    def test_register_creates_viewer_role_by_default(self):
        """A new user must always start as 'viewer', even if they try to send role=admin."""
        payload = {
            "email": "newuser@example.com",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "password": "StrongPass123!",
            "password2": "StrongPass123!",
            "role": "admin",  # attempted privilege escalation
        }
        response = self.client.post("/api/auth/register/", payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="newuser@example.com")
        self.assertEqual(user.role, User.Role.VIEWER)

    def test_register_fails_on_password_mismatch(self):
        payload = {
            "email": "mismatch@example.com",
            "username": "mismatch",
            "password": "StrongPass123!",
            "password2": "DifferentPass123!",
        }
        response = self.client.post("/api/auth/register/", payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="loginuser", email="login@example.com",
            password="StrongPass123!", role=User.Role.ASSESSOR,
        )

    def test_login_returns_jwt_tokens(self):
        response = self.client.post("/api/auth/login/", {
            "email": "login@example.com", "password": "StrongPass123!",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_fails_with_wrong_password(self):
        response = self.client.post("/api/auth/login/", {
            "email": "login@example.com", "password": "WrongPassword",
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileAndAdminAccessTests(APITestCase):
    def setUp(self):
        self.viewer = User.objects.create_user(
            username="viewer1", email="viewer1@example.com",
            password="Pass123!", role=User.Role.VIEWER,
        )
        self.admin = User.objects.create_user(
            username="admin1", email="admin1@example.com",
            password="Pass123!", role=User.Role.ADMIN,
        )

    def test_profile_requires_authentication(self):
        response = self.client.get("/api/auth/profile/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_view_own_profile(self):
        self.client.force_authenticate(self.viewer)
        response = self.client.get("/api/auth/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "viewer1@example.com")

    def test_non_admin_cannot_list_all_users(self):
        self.client.force_authenticate(self.viewer)
        response = self.client.get("/api/auth/admin/users/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_list_all_users(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get("/api/auth/admin/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
'''

with open("apps/accounts/tests.py", "w") as f:
    f.write(accounts_tests)

# ============================================================
# INSTITUTIONS TESTS
# ============================================================
institutions_tests = '''from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.institutions.models import Institution

User = get_user_model()


class InstitutionRBACTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin2", email="admin2@example.com", password="Pass123!",
            role=User.Role.ADMIN,
        )
        self.assessor = User.objects.create_user(
            username="assessor2", email="assessor2@example.com", password="Pass123!",
            role=User.Role.ASSESSOR, organization="GTBank",
        )
        self.viewer_other_org = User.objects.create_user(
            username="viewer2", email="viewer2@example.com", password="Pass123!",
            role=User.Role.VIEWER, organization="Kuda",
        )
        self.gtbank = Institution.objects.create(
            name="GTBank", type=Institution.InstitutionType.BANK,
            registration_number="RC-001", email="risk@gtbank.com",
            created_by=self.admin,
        )
        self.kuda = Institution.objects.create(
            name="Kuda", type=Institution.InstitutionType.FINTECH,
            registration_number="RC-002", email="risk@kuda.com",
            created_by=self.admin,
        )

    def test_admin_sees_all_institutions(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get("/api/institutions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_assessor_only_sees_own_institution(self):
        """RBAC: an assessor at GTBank must not see Kuda's data."""
        self.client.force_authenticate(self.assessor)
        response = self.client.get("/api/institutions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [i["name"] for i in response.data["results"]]
        self.assertIn("GTBank", names)
        self.assertNotIn("Kuda", names)

    def test_viewer_cannot_create_institution(self):
        self.client.force_authenticate(self.viewer_other_org)
        response = self.client.post("/api/institutions/", {
            "name": "New Fintech", "type": "fintech",
            "registration_number": "RC-999", "email": "x@x.com",
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_institution(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post("/api/institutions/", {
            "name": "New Fintech", "type": "fintech",
            "registration_number": "RC-999", "email": "x@x.com",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Institution.objects.filter(name="New Fintech").exists())
'''

with open("apps/institutions/tests.py", "w") as f:
    f.write(institutions_tests)

# ============================================================
# ASSESSMENTS TESTS
# ============================================================
assessments_tests = '''from django.contrib.auth import get_user_model
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
'''

with open("apps/assessments/tests.py", "w") as f:
    f.write(assessments_tests)

# ============================================================
# RISK ENGINE TESTS
# ============================================================
risk_engine_tests = '''from types import SimpleNamespace
from django.test import SimpleTestCase
from apps.risk_engine.scoring import RiskScoringEngine


def make_response(category, score, weight=1.0):
    """A lightweight stand-in for AssessmentResponse, so these are fast unit
    tests that don't need the database."""
    question = SimpleNamespace(
        category=category, weight=weight,
        question_text=f"{category} control", framework_reference="TEST-1",
    )
    return SimpleNamespace(
        question=question, score=score,
        get_score_display=lambda: str(score),
    )


class RiskScoringEngineTests(SimpleTestCase):
    """
    Unit tests for Objective 2: the risk scoring framework.
    These check the maths directly, independent of the web layer.
    """

    def setUp(self):
        self.engine = RiskScoringEngine()

    def test_category_score_is_100_when_all_answers_are_maximum(self):
        responses = [make_response("authentication", 5), make_response("authentication", 5)]
        score = self.engine.calculate_category_score(responses, "authentication")
        self.assertEqual(score, 100.0)

    def test_category_score_is_0_when_all_answers_are_minimum(self):
        responses = [make_response("authentication", 0)]
        score = self.engine.calculate_category_score(responses, "authentication")
        self.assertEqual(score, 0.0)

    def test_category_score_is_none_when_category_has_no_responses(self):
        responses = [make_response("authentication", 5)]
        score = self.engine.calculate_category_score(responses, "encryption")
        self.assertIsNone(score)

    def test_overall_score_is_weighted_average_of_categories(self):
        category_scores = {"authentication": 100, "encryption": 0}
        overall = self.engine.calculate_overall_score(category_scores)
        # weights: authentication=0.20, encryption=0.20 -> equal weight -> midpoint
        self.assertEqual(overall, 50.0)

    def test_risk_level_boundaries_are_correctly_classified(self):
        self.assertEqual(self.engine.get_risk_level(10)["level"], "critical")
        self.assertEqual(self.engine.get_risk_level(45)["level"], "high")
        self.assertEqual(self.engine.get_risk_level(60)["level"], "medium")
        self.assertEqual(self.engine.get_risk_level(75)["level"], "low")
        self.assertEqual(self.engine.get_risk_level(90)["level"], "negligible")

    def test_compliance_scores_average_the_mapped_categories(self):
        category_scores = {
            "authentication": 80, "encryption": 60, "api_security": 100,
            "data_storage": 40, "network_security": 50, "incident_response": 70,
            "third_party": 90, "compliance": 30,
        }
        compliance = self.engine.calculate_compliance_scores(category_scores)
        # owasp = avg(authentication, encryption, api_security, data_storage)
        expected_owasp = round((80 + 60 + 100 + 40) / 4, 2)
        self.assertEqual(compliance["owasp"], expected_owasp)

    def test_build_findings_flags_weak_responses_by_severity(self):
        responses = [
            make_response("authentication", 0),  # critical
            make_response("encryption", 1),       # high
            make_response("api_security", 2),     # medium
            make_response("data_storage", 4),     # not a finding (>2)
        ]
        findings = self.engine.build_findings(responses)
        self.assertEqual(len(findings["critical"]), 1)
        self.assertEqual(len(findings["high"]), 1)
        self.assertEqual(len(findings["medium"]), 1)
        self.assertEqual(len(findings["low"]), 0)

    def test_full_pipeline_score_assessment_end_to_end(self):
        assessment = SimpleNamespace()
        responses = [make_response(cat, 5) for cat in [
            "authentication", "encryption", "api_security", "data_storage",
            "network_security", "incident_response", "third_party", "compliance",
        ]]
        result = self.engine.score_assessment(assessment, responses)
        self.assertEqual(result["overall_score"], 100.0)
        self.assertEqual(result["risk_level"]["level"], "negligible")
        self.assertEqual(assessment.risk_level, "negligible")
'''

with open("apps/risk_engine/tests.py", "w") as f:
    f.write(risk_engine_tests)

print("✅ All test files created successfully!")
print("✅ __init__.py files created for all apps!")