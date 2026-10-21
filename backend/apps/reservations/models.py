import uuid
from django.conf import settings
from django.db import models
from apps.inventory.models import EquipmentItem


# This function serves to generate a short unique reservation code for front desk lookup.
def generate_reservation_code() -> str:
    return f"UCF-{uuid.uuid4().hex[:6].upper()}"


# This model serves to track student equipment reservations in 30 minute increments.
class Reservation(models.Model):
    class Status(models.TextChoices):
        RESERVED = "RESERVED", "Reserved"
        CHECKED_OUT = "CHECKED_OUT", "Checked Out"
        RETURNED = "RETURNED", "Returned"
        CANCELLED = "CANCELLED", "Cancelled"
        OVERDUE = "OVERDUE", "Overdue"

    reservation_code = models.CharField(
        max_length=12,
        unique=True,
        default=generate_reservation_code,
        editable=False,
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    equipment = models.ForeignKey(
        EquipmentItem,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    quantity = models.PositiveIntegerField(default=1)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.RESERVED,
    )
    assigned_item_tag = models.CharField(max_length=50, blank=True)
    checked_out_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="processed_checkouts",
    )
    checked_in_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="processed_returns",
    )
    checked_out_at = models.DateTimeField(null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    return_condition_notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.reservation_code} - {self.student.ucf_id} ({self.equipment.name})"