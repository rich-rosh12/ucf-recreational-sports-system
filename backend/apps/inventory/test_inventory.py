from rest_framework import status
from rest_framework.test import APITestCase
from apps.accounts.models import User
from .models import EquipmentItem


class InventoryCatalogTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin_user",
            email="admin@ucf.edu",
            password="Password123!",
            first_name="Corey",
            last_name="Pittman",
            ucf_id="9998887",
            role=User.Role.ADMIN,
            waiver_signed=True,
        )
        self.student = User.objects.create_user(
            username="student_user",
            email="student@ucf.edu",
            password="Password123!",
            first_name="Richard",
            last_name="Roshan",
            ucf_id="1234567",
            role=User.Role.STUDENT,
            waiver_signed=True,
        )
        self.item = EquipmentItem.objects.create(
            name="Wilson Evolution Basketball",
            category=EquipmentItem.Category.COURT,
            total_quantity=10,
            available_quantity=2,
            damaged_quantity=1,
        )
        self.list_url = "/api/v1/inventory/"

    def test_public_can_list_inventory_and_compute_low_stock_status(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data["results"] if isinstance(response.data, dict) and "results" in response.data else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["availability_status"], "LOW_STOCK")

    def test_only_admin_can_create_new_equipment(self):
        payload = {
            "name": "Spalding Indoor Volleyball",
            "category": EquipmentItem.Category.COURT,
            "total_quantity": 5,
            "available_quantity": 5,
        }
        self.client.force_authenticate(user=self.student)
        forbidden_res = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(forbidden_res.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.admin)
        created_res = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(created_res.status_code, status.HTTP_201_CREATED)
