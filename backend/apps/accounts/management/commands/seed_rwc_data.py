from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import User
from apps.inventory.models import EquipmentItem


# This command serves to seed demo RBAC roles and UCF RWC equipment inventory.
class Command(BaseCommand):
    help = "Seeds Student, Rec Worker, and Rec Administrator accounts plus RWC equipment."

    def handle(self, *args, **options):
        users_to_seed = [
            {
                "username": "student_jack",
                "email": "jack.richards@ucf.edu",
                "first_name": "Jack",
                "last_name": "Richards",
                "ucf_id": "4829104",
                "role": User.Role.STUDENT,
                "waiver_signed": True,
            },
            {
                "username": "worker_jane",
                "email": "jane.dumbbell@ucf.edu",
                "first_name": "Jane",
                "last_name": "Dumbbell",
                "ucf_id": "3109482",
                "role": User.Role.WORKER,
                "waiver_signed": True,
            },
            {
                "username": "admin_richard",
                "email": "ri425565@ucf.edu",
                "first_name": "Richard",
                "last_name": "Roshan",
                "ucf_id": "1049283",
                "role": User.Role.ADMIN,
                "waiver_signed": True,
            },
        ]

        for u_data in users_to_seed:
            user, created = User.objects.update_or_create(
                username=u_data["username"],
                defaults={
                    "email": u_data["email"],
                    "first_name": u_data["first_name"],
                    "last_name": u_data["last_name"],
                    "ucf_id": u_data["ucf_id"],
                    "role": u_data["role"],
                    "waiver_signed": u_data["waiver_signed"],
                    "waiver_signed_at": timezone.now(),
                },
            )
            user.set_password("UcfKnights2026!")
            user.save()

        equipment_catalog = [
            ("Wilson Evolution Indoor Basketball", EquipmentItem.Category.COURT, 15, 12, False),
            ("Mikasa V200W Indoor Volleyball", EquipmentItem.Category.COURT, 10, 8, False),
            ("RWC Official Dodgeball Set", EquipmentItem.Category.COURT, 16, 16, False),
            ("Wilson Pro Staff Tennis Racket", EquipmentItem.Category.RACKET, 8, 5, False),
            ("JOOLA Table Tennis Paddle & Ball Set", EquipmentItem.Category.RACKET, 12, 3, False),
            ("Yonex Badminton Racket Pair", EquipmentItem.Category.RACKET, 6, 0, False),
            ("UCF Intramural Mesh Scrimmage Jersey", EquipmentItem.Category.INTRAMURAL, 30, 27, True),
            ("Flag Football Belt & Flag Set", EquipmentItem.Category.INTRAMURAL, 24, 20, False),
            ("Wilson GST Official Football", EquipmentItem.Category.OUTDOOR, 10, 6, False),
            ("Select Numero 10 Soccer Ball", EquipmentItem.Category.OUTDOOR, 8, 2, False),
        ]

        for name, category, total, avail, needs_tag in equipment_catalog:
            EquipmentItem.objects.update_or_create(
                name=name,
                defaults={
                    "category": category,
                    "total_quantity": total,
                    "available_quantity": avail,
                    "requires_jersey_number": needs_tag,
                    "description": f"Official UCF RWC {name} available for 30-minute increment checkouts.",
                },
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded UCF RWC roles and equipment catalog!"))