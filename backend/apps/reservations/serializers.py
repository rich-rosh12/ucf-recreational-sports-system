from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers
from apps.accounts.serializers import UserSerializer
from apps.inventory.serializers import EquipmentItemSerializer
from .models import Reservation


# This serializer serves to validat 30-minute reservation slots and 7-day advance limits.
class ReservationSerializer(serializers.ModelSerializer):
    student_details = UserSerializer(source="student", read_only=True)
    equipment_details = EquipmentItemSerializer(source="equipment", read_only=True)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "reservation_code",
            "student",
            "student_details",
            "equipment",
            "equipment_details",
            "quantity",
            "start_time",
            "end_time",
            "status",
            "assigned_item_tag",
            "checked_out_at",
            "returned_at",
            "return_condition_notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "reservation_code",
            "student",
            "status",
            "assigned_item_tag",
            "checked_out_at",
            "returned_at",
            "created_at",
            "updated_at",
        ]

    # This method serves to enforce 30-minute increments and the one-week booking window.
    def validate(self, attrs):
        start_time = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end_time = attrs.get("end_time", getattr(self.instance, "end_time", None))
        quantity = attrs.get("quantity", getattr(self.instance, "quantity", 1))
        now = timezone.now()

        if quantity < 1:
            raise serializers.ValidationError({"quantity": "Quantity must be at least 1."})

        if start_time and end_time:
            if end_time <= start_time:
                raise serializers.ValidationError({"end_time": "End time must be after start time."})

            if start_time < now - timedelta(minutes=5):
                raise serializers.ValidationError({"start_time": "Cannot book reservations in the past."})

            if start_time > now + timedelta(days=7):
                raise serializers.ValidationError(
                    {"start_time": "Reservations can only be booked up to 7 days in advance."}
                )

            if start_time.minute not in (0, 30) or start_time.second != 0:
                raise serializers.ValidationError(
                    {"start_time": "Start time must be on a 30-minute boundary (e.g., 10:00 or 10:30)."}
                )

            if end_time.minute not in (0, 30) or end_time.second != 0:
                raise serializers.ValidationError(
                    {"end_time": "End time must be on a 30-minute boundary (e.g., 10:30 or 11:00)."}
                )

            duration_minutes = int((end_time - start_time).total_seconds() // 60)
            if duration_minutes < 30 or duration_minutes % 30 != 0:
                raise serializers.ValidationError(
                    {"end_time": "Reservation duration must be in 30-minute increments."}
                )

        return attrs