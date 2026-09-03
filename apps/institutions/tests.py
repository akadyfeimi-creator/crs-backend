from django.contrib.auth import get_user_model
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
