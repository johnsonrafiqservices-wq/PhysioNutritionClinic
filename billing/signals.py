from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from patients.models import Patient
from .models import Invoice


def generate_invoice_number():
    """Generate a unique invoice number"""
    last_invoice = Invoice.objects.order_by('-id').first()
    if last_invoice and last_invoice.invoice_number:
        try:
            last_number = int(last_invoice.invoice_number.split('-')[1])
            return f"INV-{last_number + 1:06d}"
        except (ValueError, IndexError):
            # If parsing fails, get the count and add 1
            invoice_count = Invoice.objects.count()
            return f"INV-{invoice_count + 1:06d}"
    else:
        return "INV-000001"


@receiver(post_save, sender=Patient)
def create_invoice_for_new_patient(sender, instance, created, **kwargs):
    """
    Automatically create an invoice when a new patient is registered.
    The invoice will be in draft status and empty, ready for services to be added.
    """
    if created:  # Only for newly created patients
        # Calculate due date (30 days from registration)
        due_date = timezone.now().date() + timedelta(days=30)
        
        # Create the invoice
        invoice = Invoice.objects.create(
            invoice_number=generate_invoice_number(),
            patient=instance,
            due_date=due_date,
            status='draft',
            subtotal=0,
            tax_rate=0,  # Can be configured based on clinic settings
            tax_amount=0,
            discount_amount=0,
            total_amount=0,
            notes=f'Automatically created for new patient registration on {timezone.now().date()}',
            created_by=instance.registered_by,
        )
        
        # Log the creation (optional - you can remove this in production)
        print(f"Automatically created invoice {invoice.invoice_number} for patient {instance.get_full_name()}")
