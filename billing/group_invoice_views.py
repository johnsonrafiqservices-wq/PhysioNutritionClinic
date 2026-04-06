"""
Views for Group Invoicing functionality
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum, Count
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from accounts.permissions import app_access_required, finance_staff_required
from .models import GroupInvoice, GroupInvoiceItem, GroupPayment
from patients.models import Patient, PatientGroup
from appointments.models import Appointment, Service
from laboratory.models import LabTestRequest


@login_required
@app_access_required('billing')
def group_invoice_list(request):
    """List all group invoices with filtering"""
    invoices = GroupInvoice.objects.select_related('patient_group', 'created_by').all()
    
    # Filters
    status = request.GET.get('status')
    group_id = request.GET.get('group')
    invoice_type = request.GET.get('type')
    
    if status:
        invoices = invoices.filter(status=status)
    if group_id:
        invoices = invoices.filter(patient_group_id=group_id)
    if invoice_type:
        invoices = invoices.filter(invoice_type=invoice_type)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(invoices, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all patient groups for filter dropdown
    patient_groups = PatientGroup.objects.filter(is_active=True).order_by('name')
    
    context = {
        'page_obj': page_obj,
        'patient_groups': patient_groups,
        'current_status': status,
        'current_group': group_id,
        'current_type': invoice_type,
    }
    return render(request, 'billing/group_invoice_list.html', context)


@login_required
@app_access_required('billing')
def group_invoice_generate(request):
    """Generate a group invoice for a specific period"""
    if request.method == 'POST':
        patient_group_id = request.POST.get('patient_group')
        period_start = request.POST.get('period_start')
        period_end = request.POST.get('period_end')
        due_date = request.POST.get('due_date')
        invoice_type = request.POST.get('invoice_type', 'auto')
        
        # Validate inputs
        if not all([patient_group_id, due_date]):
            messages.error(request, 'Patient group and due date are required.')
            return redirect('billing:group_invoice_generate')
        
        try:
            patient_group = PatientGroup.objects.get(id=patient_group_id)
            
            # Parse dates
            if period_start:
                period_start = datetime.strptime(period_start, '%Y-%m-%d').date()
            if period_end:
                period_end = datetime.strptime(period_end, '%Y-%m-%d').date()
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            
            with transaction.atomic():
                # Create the group invoice
                invoice = GroupInvoice.objects.create(
                    patient_group=patient_group,
                    invoice_type=invoice_type,
                    period_start=period_start,
                    period_end=period_end,
                    due_date=due_date,
                    created_by=request.user,
                    billing_contact_name=request.POST.get('billing_contact_name', ''),
                    billing_contact_email=request.POST.get('billing_contact_email', ''),
                    billing_contact_phone=request.POST.get('billing_contact_phone', ''),
                    billing_address=request.POST.get('billing_address', ''),
                    tax_rate=Decimal(request.POST.get('tax_rate', '0')),
                    discount_amount=Decimal(request.POST.get('discount_amount', '0')),
                    notes=request.POST.get('notes', ''),
                )
                
                # Generate invoice number
                last_invoice = GroupInvoice.objects.order_by('-id').exclude(id=invoice.id).first()
                if last_invoice and last_invoice.invoice_number.startswith('GRP-'):
                    try:
                        last_num = int(last_invoice.invoice_number.split('-')[1])
                        new_num = last_num + 1
                    except (ValueError, IndexError):
                        new_num = 1
                else:
                    new_num = 1
                invoice.invoice_number = f"GRP-{new_num:05d}"
                invoice.save()
                
                # If auto-generated, collect services from the period
                if invoice_type == 'auto' and period_start and period_end:
                    # Get all patients in this group
                    patients = Patient.objects.filter(patient_group=patient_group)
                    
                    # Collect appointments
                    appointments = Appointment.objects.filter(
                        patient__in=patients,
                        appointment_date__gte=period_start,
                        appointment_date__lte=period_end,
                        status='completed'
                    ).select_related('patient', 'service')
                    
                    for appt in appointments:
                        if appt.service:
                            # Get group-specific price or default
                            from billing.models import ServicePriceGroup
                            unit_price = ServicePriceGroup.get_price_for_patient(appt.service, appt.patient)
                            
                            GroupInvoiceItem.objects.create(
                                group_invoice=invoice,
                                patient=appt.patient,
                                service=appt.service,
                                appointment=appt,
                                service_date=appt.appointment_date,
                                description=f"{appt.service.name} - {appt.patient.get_full_name()}",
                                quantity=1,
                                unit_price=unit_price,
                            )
                    
                    # Collect lab tests
                    lab_requests = LabTestRequest.objects.filter(
                        patient__in=patients,
                        date_requested__gte=period_start,
                        date_requested__lte=period_end,
                        status='completed'
                    ).select_related('patient', 'test')
                    
                    for lab_req in lab_requests:
                        # Get group-specific price or default
                        from laboratory.models import LabTestPriceGroup
                        unit_price = LabTestPriceGroup.get_price_for_patient(lab_req.test, lab_req.patient)
                        
                        GroupInvoiceItem.objects.create(
                            group_invoice=invoice,
                            patient=lab_req.patient,
                            lab_test_request=lab_req,
                            service_date=lab_req.date_requested.date(),
                            description=f"{lab_req.test.name} - {lab_req.patient.get_full_name()}",
                            quantity=1,
                            unit_price=unit_price,
                        )
                    
                    # Calculate totals
                    invoice.calculate_totals()
                
                # If custom invoice, process manually added items
                elif invoice_type == 'custom':
                    # Parse custom items from POST data
                    # Items are submitted as items[1][description], items[1][quantity], etc.
                    items_data = {}
                    for key, value in request.POST.items():
                        if key.startswith('items['):
                            # Extract item number and field name
                            # Format: items[1][description]
                            import re
                            match = re.match(r'items\[(\d+)\]\[(\w+)\]', key)
                            if match:
                                item_num = match.group(1)
                                field_name = match.group(2)
                                
                                if item_num not in items_data:
                                    items_data[item_num] = {}
                                items_data[item_num][field_name] = value
                    
                    # Create invoice items
                    for item_num, item_fields in items_data.items():
                        if 'description' in item_fields and 'quantity' in item_fields and 'unit_price' in item_fields:
                            # Get patient if specified
                            patient = None
                            if item_fields.get('patient_id'):
                                try:
                                    patient = Patient.objects.get(id=item_fields['patient_id'])
                                except Patient.DoesNotExist:
                                    pass
                            
                            # Parse service date
                            service_date = timezone.now().date()
                            if item_fields.get('service_date'):
                                try:
                                    service_date = datetime.strptime(item_fields['service_date'], '%Y-%m-%d').date()
                                except:
                                    pass
                            
                            GroupInvoiceItem.objects.create(
                                group_invoice=invoice,
                                patient=patient,
                                service_date=service_date,
                                description=item_fields['description'],
                                quantity=Decimal(item_fields['quantity']),
                                unit_price=Decimal(item_fields['unit_price']),
                            )
                    
                    # Calculate totals
                    invoice.calculate_totals()
                
                messages.success(request, f'Group invoice {invoice.invoice_number} created successfully!')
                return redirect('billing:group_invoice_detail', pk=invoice.pk)
                
        except PatientGroup.DoesNotExist:
            messages.error(request, 'Invalid patient group selected.')
        except Exception as e:
            messages.error(request, f'Error creating invoice: {str(e)}')
            return redirect('billing:group_invoice_generate')
    
    # GET request - show form
    patient_groups = PatientGroup.objects.filter(is_active=True).order_by('name')
    
    # Suggest default period (last month)
    today = timezone.now().date()
    default_period_end = today.replace(day=1) - timedelta(days=1)  # Last day of previous month
    default_period_start = default_period_end.replace(day=1)  # First day of previous month
    default_due_date = today + timedelta(days=30)  # 30 days from today
    
    context = {
        'patient_groups': patient_groups,
        'default_period_start': default_period_start,
        'default_period_end': default_period_end,
        'default_due_date': default_due_date,
    }
    return render(request, 'billing/group_invoice_generate.html', context)


@login_required
@app_access_required('billing')
def group_invoice_detail(request, pk):
    """View and manage a specific group invoice"""
    invoice = get_object_or_404(
        GroupInvoice.objects.select_related('patient_group', 'created_by'),
        pk=pk
    )
    
    # Get all items grouped by patient
    items = invoice.items.select_related('patient', 'service', 'appointment', 'lab_test_request').order_by('patient', 'service_date')
    
    # Get payments
    payments = invoice.group_payments.all().order_by('-payment_date')
    
    # Calculate summary
    total_paid = invoice.get_total_paid()
    balance_due = invoice.get_balance_due()
    
    context = {
        'invoice': invoice,
        'items': items,
        'payments': payments,
        'total_paid': total_paid,
        'balance_due': balance_due,
    }
    return render(request, 'billing/group_invoice_detail.html', context)


@login_required
@app_access_required('billing')
def group_invoice_add_item(request, pk):
    """Add a custom item to a group invoice"""
    invoice = get_object_or_404(GroupInvoice, pk=pk)
    
    if request.method == 'POST':
        try:
            patient_id = request.POST.get('patient')
            service_date = datetime.strptime(request.POST.get('service_date'), '%Y-%m-%d').date()
            description = request.POST.get('description')
            quantity = int(request.POST.get('quantity', 1))
            unit_price = Decimal(request.POST.get('unit_price'))
            
            patient = Patient.objects.get(id=patient_id)
            
            GroupInvoiceItem.objects.create(
                group_invoice=invoice,
                patient=patient,
                service_date=service_date,
                description=description,
                quantity=quantity,
                unit_price=unit_price,
            )
            
            messages.success(request, 'Item added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding item: {str(e)}')
    
    return redirect('billing:group_invoice_detail', pk=pk)


@login_required
@app_access_required('billing')
def group_invoice_delete_item(request, pk, item_id):
    """Delete an item from a group invoice"""
    invoice = get_object_or_404(GroupInvoice, pk=pk)
    item = get_object_or_404(GroupInvoiceItem, pk=item_id, group_invoice=invoice)
    
    if request.method == 'POST':
        item.delete()
        invoice.calculate_totals()
        messages.success(request, 'Item deleted successfully!')
    
    return redirect('billing:group_invoice_detail', pk=pk)


@login_required
@app_access_required('billing')
def group_invoice_add_payment(request, pk):
    """Record a payment against a group invoice"""
    invoice = get_object_or_404(GroupInvoice, pk=pk)
    
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount'))
            payment_method = request.POST.get('payment_method')
            reference_number = request.POST.get('reference_number', '')
            notes = request.POST.get('notes', '')
            
            # Generate payment ID
            last_payment = GroupPayment.objects.order_by('-id').first()
            if last_payment and last_payment.payment_id.startswith('GRPPAY-'):
                try:
                    last_num = int(last_payment.payment_id.split('-')[1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1
            payment_id = f"GRPPAY-{new_num:05d}"
            
            payment = GroupPayment.objects.create(
                payment_id=payment_id,
                group_invoice=invoice,
                amount=amount,
                payment_method=payment_method,
                reference_number=reference_number,
                notes=notes,
                status='completed',
                processed_by=request.user,
            )
            
            # Update invoice status if fully paid
            if invoice.get_balance_due() <= 0:
                invoice.status = 'paid'
            elif invoice.get_total_paid() > 0:
                invoice.status = 'partial'
            invoice.save()
            
            messages.success(request, f'Payment {payment_id} recorded successfully!')
        except Exception as e:
            messages.error(request, f'Error recording payment: {str(e)}')
    
    return redirect('billing:group_invoice_detail', pk=pk)


@login_required
@app_access_required('billing')
def group_payment_receipt(request, pk):
    """Print receipt for a group invoice payment"""
    from billing.models import GroupPayment
    payment = get_object_or_404(GroupPayment.objects.select_related('group_invoice__patient_group', 'processed_by'), pk=pk)

    from clinic_settings.models import ClinicSettings
    try:
        clinic_settings = ClinicSettings.objects.first()
    except Exception:
        clinic_settings = None

    context = {
        'payment': payment,
        'clinic_settings': clinic_settings,
        'qr_code': None,
        'cloud_url': payment.receipt_pdf_url,
        'gdrive_url': payment.gdrive_pdf_url,
    }
    return render(request, 'billing/payment_receipt.html', context)


@login_required
@app_access_required('billing')
def group_invoice_print(request, pk):
    """Print view for group invoice"""
    invoice = get_object_or_404(
        GroupInvoice.objects.select_related('patient_group', 'created_by'),
        pk=pk
    )
    
    # Get all items grouped by patient
    from itertools import groupby
    items = invoice.items.select_related('patient', 'service').order_by('patient__first_name', 'patient__last_name', 'service_date')
    
    # Group items by patient
    items_by_patient = {}
    for patient, patient_items in groupby(items, key=lambda x: x.patient):
        items_by_patient[patient] = list(patient_items)
    
    # Get clinic settings
    from clinic_settings.models import ClinicSettings
    clinic_settings = ClinicSettings.objects.first()
    
    context = {
        'invoice': invoice,
        'items_by_patient': items_by_patient,
        'clinic_settings': clinic_settings,
        'total_paid': invoice.get_total_paid(),
        'balance_due': invoice.get_balance_due(),
    }
    return render(request, 'billing/group_invoice_print.html', context)
