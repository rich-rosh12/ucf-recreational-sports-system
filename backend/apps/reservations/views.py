from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.accounts.permissions import IsRecWorkerOrAdmin
from apps.inventory.models import EquipmentItem
from .models import Reservation
from .serializers import ReservationSerializer


# This viewset serves to handel student bookings, edits, cancelations, and worker checkouts.
class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    # This method serves to filter reservations by role or search query for front desk staff.
    def get_queryset(self):
        user = self.request.user
        queryset = Reservation.objects.select_related("student", "equipment").order_by("-start_time")

        if user.role == "STUDENT":
            return queryset.filter(student=user)

        search_query = self.request.query_params.get("search", "").strip()
        if search_query:
            queryset = queryset.filter(
                Q(student__ucf_id__icontains=search_query)
                | Q(student__first_name__icontains=search_query)
                | Q(student__last_name__icontains=search_query)
                | Q(reservation_code__icontains=search_query)
            )
        return queryset

    # This method serves to atomically lock inventory and create a new student reservaton.
    def perform_create(self, serializer):
        user = self.request.user
        if not user.waiver_signed:
            raise ValidationError({"waiver": "You must sign the RWC digital liability waiver before reserving equipment."})
        if user.has_account_hold:
            raise PermissionDenied("Your account currently has a hold due to overdue equipment.")

        with transaction.atomic():
            equipment = EquipmentItem.objects.select_for_update().get(
                pk=serializer.validated_data["equipment"].pk
            )
            requested_qty = serializer.validated_data["quantity"]

            if not equipment.is_active or equipment.available_quantity < requested_qty:
                raise ValidationError(
                    {"quantity": f"Only {equipment.available_quantity} unit(s) of {equipment.name} currently available."}
                )

            equipment.available_quantity -= requested_qty
            equipment.save(update_fields=["available_quantity", "updated_at"])
            serializer.save(student=user, status=Reservation.Status.RESERVED)

    # This method serves to allow students to modify their reservation time or quantity safely.
    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.status != Reservation.Status.RESERVED:
            raise ValidationError({"status": "Only active RESERVED bookings can be modified."})

        with transaction.atomic():
            equipment = EquipmentItem.objects.select_for_update().get(pk=instance.equipment.pk)
            new_qty = serializer.validated_data.get("quantity", instance.quantity)
            qty_diff = new_qty - instance.quantity

            if qty_diff > 0 and equipment.available_quantity < qty_diff:
                raise ValidationError(
                    {"quantity": f"Cannot increase quantity. Only {equipment.available_quantity} additional unit(s) available."}
                )

            equipment.available_quantity -= qty_diff
            equipment.save(update_fields=["available_quantity", "updated_at"])
            serializer.save()

    # This action serves to cancel an existing reservation and restore stock counts immediately.
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        if reservation.status != Reservation.Status.RESERVED:
            return Response(
                {"detail": "Only reservations in RESERVED status can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            equipment = EquipmentItem.objects.select_for_update().get(pk=reservation.equipment.pk)
            equipment.available_quantity += reservation.quantity
            equipment.save(update_fields=["available_quantity", "updated_at"])

            reservation.status = Reservation.Status.CANCELLED
            reservation.save(update_fields=["status", "updated_at"])

        return Response(ReservationSerializer(reservation).data, status=status.HTTP_200_OK)

    # This action serves to allow front desk rec workers to check out equipment to a student.
    @action(detail=True, methods=["post"], permission_classes=[IsRecWorkerOrAdmin])
    def checkout(self, request, pk=None):
        reservation = self.get_object()
        if reservation.status != Reservation.Status.RESERVED:
            return Response(
                {"detail": "Reservation must be in RESERVED state to check out."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reservation.status = Reservation.Status.CHECKED_OUT
        reservation.assigned_item_tag = request.data.get("assigned_item_tag", "")
        reservation.checked_out_by = request.user
        reservation.checked_out_at = timezone.now()
        reservation.save()

        return Response(ReservationSerializer(reservation).data, status=status.HTTP_200_OK)

    # This action serves to allow front desk rec workers to check in returned equipment.
    @action(detail=True, methods=["post"], permission_classes=[IsRecWorkerOrAdmin])
    def checkin(self, request, pk=None):
        reservation = self.get_object()
        if reservation.status not in [Reservation.Status.CHECKED_OUT, Reservation.Status.OVERDUE]:
            return Response(
                {"detail": "Only checked-out equipment can be returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_damaged = bool(request.data.get("is_damaged", False))
        notes = request.data.get("return_condition_notes", "")

        with transaction.atomic():
            equipment = EquipmentItem.objects.select_for_update().get(pk=reservation.equipment.pk)
            if is_damaged:
                equipment.damaged_quantity += reservation.quantity
            else:
                equipment.available_quantity += reservation.quantity
            equipment.save(update_fields=["available_quantity", "damaged_quantity", "updated_at"])

            reservation.status = Reservation.Status.RETURNED
            reservation.checked_in_by = request.user
            reservation.returned_at = timezone.now()
            reservation.return_condition_notes = notes
            reservation.save()

        return Response(ReservationSerializer(reservation).data, status=status.HTTP_200_OK)