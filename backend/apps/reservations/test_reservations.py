from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from apps.accounts.models import User
from apps.inventory.models import EquipmentItem
from .models import Reservation


# This test suite serves to test 30-minute reservation rules and inventory concurrency.
class ReservationEngineTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username="jack_student",
            email="jack@ucf.edu",
            password="Password123!",
            first_name="Jack",
            last_name="Richards",
            ucf_id="1112223",
            role=User.Role.STUDENT,
            waiver_signed=True,
        )
        self.worker = User.objects.create_user(
            username="jane_worker",
            email="jane@ucf.edu",
            password="Password123!",
            first_name="Jane",
            last_name="Dumbbell",
            ucf_id="4445556",
            role=User.Role.WORKER,
            waiver_signed=True,
        )
        self.basketball = EquipmentItem.objects.create(
            name="Indoor Basketball",
            category=EquipmentItem.Category.COURT,
            total_quantity=5,
            available_quantity=5,
        )
        self.list_url = reverse("reservation-list")

    # This helper function serves to calculate the next valid 30-minute boundary timestamp.
    # This helper function serves to calculate the next valid 30-minute boundary timestamp.
    def _next_valid_slot(self, days_ahead=1):
        base = (timezone.now() + timedelta(days=days_ahead)).replace(
            hour=14, minute=0, second=0, microsecond=0
        )
        return base

    # This test serves to verify a valid 30-minute reservation decrements available stock.
    def test_create_valid_30_min_reservation_decrements_stock(self):
        self.client.force_authenticate(user=self.student)
        start = self._next_valid_slot(days_ahead=1)
        end = start + timedelta(minutes=30)

        response = self.client.post(
            self.list_url,
            {
                "equipment": self.basketball.id,
                "quantity": 2,
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.basketball.refresh_from_db()
        self.assertEqual(self.basketball.available_quantity, 3)

    # This test serves to reject reservations that do not align to 30-minute increments.
    def test_reject_non_30_minute_increment_booking(self):
        self.client.force_authenticate(user=self.student)
        start = self._next_valid_slot(days_ahead=1).replace(minute=15)
        end = start + timedelta(minutes=30)

        response = self.client.post(
            self.list_url,
            {
                "equipment": self.basketball.id,
                "quantity": 1,
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # This test serves to prevent students from booking more than 7 days in advance.
    def test_reject_booking_more_than_7_days_in_advance(self):
        self.client.force_authenticate(user=self.student)
        start = self._next_valid_slot(days_ahead=8)
        end = start + timedelta(minutes=60)

        response = self.client.post(
            self.list_url,
            {
                "equipment": self.basketball.id,
                "quantity": 1,
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # This test serves to ensure students can modify an existing reservation quantity and time.
    def test_student_can_modify_reservation_and_adjust_inventory(self):
        self.client.force_authenticate(user=self.student)
        start = self._next_valid_slot(days_ahead=1)
        end = start + timedelta(minutes=30)

        create_res = self.client.post(
            self.list_url,
            {
                "equipment": self.basketball.id,
                "quantity": 1,
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
            },
            format="json",
        )
        res_id = create_res.data["id"]
        detail_url = reverse("reservation-detail", args=[res_id])

        new_end = start + timedelta(minutes=60)
        patch_res = self.client.patch(
            detail_url,
            {"quantity": 3, "end_time": new_end.isoformat()},
            format="json",
        )
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.basketball.refresh_from_db()
        self.assertEqual(self.basketball.available_quantity, 2)

    # This test serves to verify the full worker checkout and checkin lifecycle.
    def test_worker_checkout_and_checkin_restores_inventory(self):
        self.client.force_authenticate(user=self.student)
        start = self._next_valid_slot(days_ahead=1)
        end = start + timedelta(minutes=60)

        create_res = self.client.post(
            self.list_url,
            {
                "equipment": self.basketball.id,
                "quantity": 2,
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
            },
            format="json",
        )
        res_id = create_res.data["id"]

        self.client.force_authenticate(user=self.worker)
        checkout_url = reverse("reservation-checkout", args=[res_id])
        co_res = self.client.post(checkout_url, {"assigned_item_tag": "BBALL-04"}, format="json")
        self.assertEqual(co_res.status_code, status.HTTP_200_OK)
        self.assertEqual(co_res.data["status"], Reservation.Status.CHECKED_OUT)

        checkin_url = reverse("reservation-checkin", args=[res_id])
        ci_res = self.client.post(checkin_url, {"is_damaged": False}, format="json")
        self.assertEqual(ci_res.status_code, status.HTTP_200_OK)
        self.basketball.refresh_from_db()
        self.assertEqual(self.basketball.available_quantity, 5)