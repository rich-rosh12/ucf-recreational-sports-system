from django.core.exceptions import ValidationError
from django.db import models


# This model serves to store equpment items and real-time stock counts for the rec center.
class EquipmentItem(models.Model):
    class Category(models.TextChoices):
        COURT = "COURT", "Court Sports"
        RACKET = "RACKET", "Racket & Paddle Sports"
        INTRAMURAL = "INTRAMURAL", "Intramural Jerseys & Belts"
        OUTDOOR = "OUTDOOR", "Outdoor & Field Gear"

    name = models.CharField(max_length=120, unique=True)
    category = models.CharField(max_length=25, choices=Category.choices, default=Category.COURT)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    total_quantity = models.PositiveIntegerField(default=1)
    available_quantity = models.PositiveIntegerField(default=1)
    damaged_quantity = models.PositiveIntegerField(default=0)
    requires_jersey_number = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    # This method serves to validat that available stock never exceeds total inventory.
    def clean(self):
        if self.available_quantity > self.total_quantity:
            raise ValidationError("Available quantity cannot exceed total quantity.")

    # This property serves to compute the semantic availability status for UI badges.
    @property
    def availability_status(self) -> str:
        if not self.is_active or self.available_quantity == 0:
            return "UNAVAILABLE"
        if self.available_quantity <= 3:
            return "LOW_STOCK"
        return "AVAILABLE"

    def __str__(self) -> str:
        return f"{self.name} ({self.available_quantity}/{self.total_quantity})"