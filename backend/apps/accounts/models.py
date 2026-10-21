from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


# This model serves to store user accounts and role permissions for the system.
class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "STUDENT", "Student"
        WORKER = "WORKER", "Rec Worker"
        ADMIN = "ADMIN", "Rec Administrator"

    ucf_id_validator = RegexValidator(
        regex=r"^\d{7}$",
        message="UCF ID must be exactly 7 digits.",
    )

    email = models.EmailField(unique=True)
    ucf_id = models.CharField(
        max_length=7,
        unique=True,
        validators=[ucf_id_validator],
    )
    role = models.CharField(
        max_length=15,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    waiver_signed = models.BooleanField(default=False)
    waiver_signed_at = models.DateTimeField(null=True, blank=True)
    has_account_hold = models.BooleanField(default=False)

    REQUIRED_FIELDS = ["email", "ucf_id", "first_name", "last_name"]

    # This method serves to return a readable string representation of the user.
    def __str__(self) -> str:
        return f"{self.get_full_name()} ({self.ucf_id}) - {self.role}"