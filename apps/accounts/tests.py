import uuid
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
