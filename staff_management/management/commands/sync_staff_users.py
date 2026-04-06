from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from staff_management.models import Staff


class Command(BaseCommand):
    help = (
        "Ensure every User has a Staff profile and sync active flags. "
        "Safe to run multiple times; it only creates missing Staff entries."
    )

    def handle(self, *args, **options):
        User = get_user_model()

        users = User.objects.all().order_by('id')
        created_count = 0
        synced_count = 0

        today = timezone.now().date()

        for user in users:
            # Skip superusers with no real clinic role if you prefer; for now include all
            staff = getattr(user, 'staff_profile', None)

            if staff is None:
                # Generate a simple employee ID: EMC-<user_id>
                employee_id = f"EMC-{user.id:05d}"

                staff = Staff.objects.create(
                    user=user,
                    employee_id=employee_id,
                    department=None,
                    position=user.get_role_display() if hasattr(user, 'get_role_display') else 'Staff',
                    employment_status='full_time',
                    joining_date=today,
                    is_active=user.is_active,
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f"Created Staff profile for user '{user.username}' (employee_id={employee_id})."
                ))
            else:
                # Keep staff active flag in sync with user
                if staff.is_active != user.is_active:
                    staff.is_active = user.is_active
                    staff.save(update_fields=['is_active'])
                    synced_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Sync complete. Created {created_count} Staff records; synced active flag for {synced_count} existing staff."
        ))
