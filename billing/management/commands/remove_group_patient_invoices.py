"""
Management command to permanently delete all individual invoices
(and their related line items, payments, etc.) for patients that
belong to a PatientGroup.

Usage:
    python manage.py remove_group_patient_invoices          # dry-run
    python manage.py remove_group_patient_invoices --apply  # actually delete
"""
from django.core.management.base import BaseCommand
from billing.models import Invoice


class Command(BaseCommand):
    help = 'Delete individual invoices for patients belonging to a group'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Actually delete the invoices. Without this flag the command only prints what would be removed.',
        )

    def handle(self, *args, **options):
        qs = Invoice.objects.filter(patient__patient_group__isnull=False)
        count = qs.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS('No individual invoices found for group patients. Nothing to do.'))
            return

        self.stdout.write(f'Found {count} individual invoice(s) for patients belonging to a group.')

        if not options['apply']:
            # Dry-run: list them
            for inv in qs.select_related('patient', 'patient__patient_group')[:50]:
                self.stdout.write(
                    f'  {inv.invoice_number}  |  {inv.patient.get_full_name()}  |  '
                    f'Group: {inv.patient.patient_group.name}  |  '
                    f'Status: {inv.status}  |  Total: {inv.total_amount}'
                )
            if count > 50:
                self.stdout.write(f'  ... and {count - 50} more')
            self.stdout.write(self.style.WARNING(
                '\nThis is a DRY RUN. Re-run with --apply to actually delete these invoices.'
            ))
            return

        # Cascade delete (line items, payments, audit logs, etc.)
        deleted = qs.delete()
        self.stdout.write(self.style.SUCCESS(
            f'Deleted {deleted[0]} object(s): {deleted[1]}'
        ))
