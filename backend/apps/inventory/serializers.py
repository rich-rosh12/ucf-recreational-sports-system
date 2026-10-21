from rest_framework import serializers
from .models import EquipmentItem


# This serializer serves to transform equipment inventory models into JSON responses.
class EquipmentItemSerializer(serializers.ModelSerializer):
    availability_status = serializers.ReadOnlyField()

    class Meta:
        model = EquipmentItem
        fields = [
            "id",
            "name",
            "category",
            "description",
            "image_url",
            "total_quantity",
            "available_quantity",
            "damaged_quantity",
            "requires_jersey_number",
            "is_active",
            "availability_status",
            "updated_at",
        ]

    # This method serves to ensure available stock stays within total stock bounds.
    def validate(self, attrs):
        total = attrs.get("total_quantity", getattr(self.instance, "total_quantity", 0))
        avail = attrs.get("available_quantity", getattr(self.instance, "available_quantity", 0))
        if avail > total:
            raise serializers.ValidationError("Available quantity cannot exceed total quantity.")
        return attrs