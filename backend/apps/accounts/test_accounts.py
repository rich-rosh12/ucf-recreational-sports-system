from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User


# This test suite serves to verify JWT authentication and RBAC role switching logic.
class AccountsRBACTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username="student1",
            email="student1@ucf.edu",
            password="Password123!",
            first_name="Kane",
            last_name="Price",
            ucf_id="1234567",
            role=User.Role.STUDENT,
        )
        self.admin = User.objects.create_user(
            username="admin1",
            email="admin1@ucf.edu",
            password="Password123!",
            first_name="Richard",
            last_name="Roshan",
            ucf_id="7654321",
            role=User.Role.ADMIN,
        )

    # This test serves to validat that the 1-click role switcher returns valid JWT tokens.
    def test_one_click_demo_role_switcher(self):
        url = reverse("demo_role_login")
        response = self.client.post(url, {"role": "ADMIN"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertEqual(response.data["user"]["role"], "ADMIN")

    # This test serves to confirm that signing the digital waiver updates the student profile.
    def test_student_can_sign_digital_waiver(self):
        self.client.force_authenticate(user=self.student)
        url = reverse("sign_waiver")
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["waiver_signed"])