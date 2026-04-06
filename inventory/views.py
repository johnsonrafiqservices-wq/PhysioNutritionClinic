from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Drug, DrugUsage, CashFlow, Supplier
from .forms import DrugForm, DrugUsageForm, CashFlowForm, SupplierForm

# List all drugs
def drug_list(request):
	drugs = Drug.objects.select_related('supplier').all()
	# Add data required for modals
	suppliers = Supplier.objects.all().order_by('name')
	return render(request, 'inventory/drug_list.html', {
		'drugs': drugs,
		'suppliers': suppliers
	})

# Add or edit a drug
def drug_edit(request, pk=None):
	drug = get_object_or_404(Drug, pk=pk) if pk else None
	if request.method == 'POST':
		form = DrugForm(request.POST, instance=drug)
		if form.is_valid():
			form.save()
			# Check if AJAX request
			if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
				return JsonResponse({
					'success': True,
					'message': 'Drug saved successfully!'
				})
			return redirect('inventory:drug_list')
		else:
			# Return errors for AJAX
			if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
				return JsonResponse({
					'success': False,
					'errors': form.errors
				}, status=400)
	else:
		form = DrugForm(instance=drug)
	return render(request, 'inventory/drug_edit.html', {'form': form})

# Add or edit a supplier
def supplier_edit(request, pk=None):
	supplier = get_object_or_404(Supplier, pk=pk) if pk else None
	if request.method == 'POST':
		form = SupplierForm(request.POST, instance=supplier)
		if form.is_valid():
			form.save()
			# Check if AJAX request
			if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
				return JsonResponse({
					'success': True,
					'message': 'Supplier saved successfully!'
				})
			return redirect('inventory:drug_list')
		else:
			# Return errors for AJAX
			if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
				return JsonResponse({
					'success': False,
					'errors': form.errors
				}, status=400)
	else:
		form = SupplierForm(instance=supplier)
	return render(request, 'inventory/supplier_edit.html', {'form': form})

# Record drug usage or sale
def record_usage(request):
	if request.method == 'POST':
		form = DrugUsageForm(request.POST)
		if form.is_valid():
			usage = form.save()
			# Update drug quantity
			usage.drug.quantity -= usage.used_quantity
			usage.drug.save()
			# Record cash flow
			if usage.usage_type == 'sale':
				CashFlow.objects.create(drug=usage.drug, amount=usage.sale_price or 0, currency=usage.currency, flow_type='in', description=f"Sale to {usage.sold_to}", country=usage.country)
			else:
				CashFlow.objects.create(drug=usage.drug, amount=usage.used_quantity * usage.drug.unit_price, currency=usage.currency, flow_type='out', description=f"Used for {usage.used_for}", country=usage.country)
			# Check if AJAX request
			if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
				return JsonResponse({
					'success': True,
					'message': 'Usage recorded successfully!'
				})
			return redirect('inventory:drug_list')
		else:
			# Return errors for AJAX
			if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
				return JsonResponse({
					'success': False,
					'errors': form.errors
				}, status=400)
	else:
		form = DrugUsageForm()
	return render(request, 'inventory/record_usage.html', {'form': form})

# Cash flow list
def cashflow_list(request):
	flows = CashFlow.objects.select_related('drug').all().order_by('-date')
	# Add data required for modals
	drugs = Drug.objects.select_related('supplier').all()
	suppliers = Supplier.objects.all().order_by('name')
	return render(request, 'inventory/cashflow_list.html', {
		'flows': flows,
		'drugs': drugs,
		'suppliers': suppliers
	})

# Sales Dashboard - Using Pharmacy Stock Movements
def sales_dashboard(request):
	from django.db.models import Sum, Count, F
	from datetime import timedelta
	from django.utils import timezone
	from pharmacy.models import StockMovement, Medication, Batch
	
	# Get sales data (stock movements marked as 'out' with sale reference)
	sales = StockMovement.objects.filter(
		movement_type='out',
		reference__icontains='SALE'
	).select_related('batch__medication', 'created_by').order_by('-created_at')
	
	# Calculate statistics
	total_sales = sales.count()
	today = timezone.now().date()
	today_sales = sales.filter(created_at__date=today).count()
	week_start = today - timedelta(days=today.weekday())
	week_sales = sales.filter(created_at__date__gte=week_start).count()
	month_sales = sales.filter(created_at__year=today.year, created_at__month=today.month).count()
	
	# Revenue calculations (quantity * selling_price from batch)
	sales_with_revenue = sales.annotate(
		revenue=F('quantity') * F('batch__selling_price')
	)
	total_revenue = sales_with_revenue.aggregate(total=Sum('revenue'))['total'] or 0
	today_revenue = sales_with_revenue.filter(created_at__date=today).aggregate(total=Sum('revenue'))['total'] or 0
	week_revenue = sales_with_revenue.filter(created_at__date__gte=week_start).aggregate(total=Sum('revenue'))['total'] or 0
	month_revenue = sales_with_revenue.filter(created_at__year=today.year, created_at__month=today.month).aggregate(total=Sum('revenue'))['total'] or 0
	
	# Top selling medications
	top_drugs = sales.values('batch__medication__name').annotate(
		total_quantity=Sum('quantity'),
		total_revenue=Sum(F('quantity') * F('batch__selling_price')),
		sales_count=Count('id')
	).order_by('-total_quantity')[:5]
	
	# Recent sales with revenue annotation
	recent_sales = sales.annotate(
		revenue=F('quantity') * F('batch__selling_price')
	)[:10]
	
	# Get available batches for sale modal
	available_batches = Batch.objects.filter(
		is_active=True,
		quantity_remaining__gt=0,
		expiry_date__gt=timezone.now()
	).select_related('medication').order_by('medication__name', 'expiry_date')
	
	context = {
		'total_sales': total_sales,
		'today_sales': today_sales,
		'week_sales': week_sales,
		'month_sales': month_sales,
		'total_revenue': total_revenue,
		'today_revenue': today_revenue,
		'week_revenue': week_revenue,
		'month_revenue': month_revenue,
		'top_drugs': top_drugs,
		'recent_sales': recent_sales,
		'available_batches': available_batches,
	}
	return render(request, 'inventory/sales_dashboard.html', context)

# Sales List - Using Pharmacy Stock Movements
def sales_list(request):
	from pharmacy.models import StockMovement
	
	sales = StockMovement.objects.filter(
		movement_type='out',
		reference__icontains='SALE'
	).select_related('batch__medication', 'created_by').order_by('-created_at')
	
	# Filter by date range if provided
	start_date = request.GET.get('start_date')
	end_date = request.GET.get('end_date')
	
	if start_date:
		sales = sales.filter(created_at__date__gte=start_date)
	if end_date:
		sales = sales.filter(created_at__date__lte=end_date)
	
	context = {
		'sales': sales,
		'start_date': start_date,
		'end_date': end_date,
	}
	return render(request, 'inventory/sales_list.html', context)

# Sales Report - Using Pharmacy Stock Movements
def sales_report(request):
	from django.db.models import Sum, Count, Avg, F, DecimalField, ExpressionWrapper
	from django.db.models.functions import TruncDate
	from datetime import timedelta
	from django.utils import timezone
	from pharmacy.models import StockMovement
	
	# Get date range from request
	start_date = request.GET.get('start_date')
	end_date = request.GET.get('end_date')
	
	today = timezone.now().date()
	if not start_date:
		start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
	if not end_date:
		end_date = today.strftime('%Y-%m-%d')
	
	# Filter sales by date range
	sales = StockMovement.objects.filter(
		movement_type='out',
		reference__icontains='SALE',
		created_at__date__gte=start_date,
		created_at__date__lte=end_date
	).select_related('batch__medication', 'created_by')
	
	# Annotate with revenue
	sales_with_revenue = sales.annotate(
		revenue=ExpressionWrapper(
			F('quantity') * F('batch__selling_price'),
			output_field=DecimalField(max_digits=12, decimal_places=2)
		)
	)
	
	# Summary statistics
	total_sales = sales.count()
	total_revenue = sales_with_revenue.aggregate(total=Sum('revenue'))['total'] or 0
	total_quantity = sales.aggregate(total=Sum('quantity'))['total'] or 0
	avg_sale_value = sales_with_revenue.aggregate(avg=Avg('revenue'))['avg'] or 0
	
	# Sales by medication - First annotate revenue on each record, then aggregate
	sales_by_drug_raw = sales_with_revenue.values(
		'batch__medication__name'
	).annotate(
		quantity=Sum('quantity'),
		revenue=Sum('revenue'),
		count=Count('id')
	).order_by('-revenue')
	
	# Convert to list to ensure it's evaluated
	sales_by_drug = list(sales_by_drug_raw)
	
	# Daily sales trend - First annotate revenue, then group by date
	daily_sales_raw = sales_with_revenue.annotate(
		date=TruncDate('created_at')
	).values('date').annotate(
		count=Count('id'),
		revenue=Sum('revenue')
	).order_by('date')
	
	# Convert to list to ensure it's evaluated
	daily_sales = list(daily_sales_raw)
	
	context = {
		'start_date': start_date,
		'end_date': end_date,
		'total_sales': total_sales,
		'total_revenue': total_revenue,
		'total_quantity': total_quantity,
		'avg_sale_value': avg_sale_value,
		'sales_by_drug': sales_by_drug,
		'daily_sales': daily_sales,
	}
	return render(request, 'inventory/sales_report.html', context)

# Record Sale AJAX
def record_sale_ajax(request):
	from django.views.decorators.http import require_POST
	from django.contrib.auth.decorators import login_required
	from pharmacy.models import StockMovement, Batch
	
	if request.method == 'POST':
		try:
			batch_id = request.POST.get('batch_id')
			quantity = int(request.POST.get('quantity', 0))
			customer_name = request.POST.get('customer_name', 'Walk-in Customer')
			notes = request.POST.get('notes', '')
			
			# Validate inputs
			if not batch_id or quantity <= 0:
				return JsonResponse({
					'success': False,
					'message': 'Please provide valid batch and quantity.'
				})
			
			# Get the batch
			batch = Batch.objects.select_related('medication').get(id=batch_id, is_active=True)
			
			# Check if enough stock
			if batch.quantity_remaining < quantity:
				return JsonResponse({
					'success': False,
					'message': f'Insufficient stock. Only {batch.quantity_remaining} units available.'
				})
			
			# Create stock movement for sale
			reference = f'SALE-{customer_name}-{timezone.now().strftime("%Y%m%d%H%M%S")}'
			stock_movement = StockMovement.objects.create(
				batch=batch,
				movement_type='out',
				quantity=quantity,
				reference=reference,
				notes=notes,
				created_by=request.user
			)
			
			# Update batch quantity
			batch.quantity_remaining -= quantity
			batch.save()
			
			# Calculate revenue
			revenue = quantity * batch.selling_price
			
			return JsonResponse({
				'success': True,
				'message': f'Sale recorded successfully! {quantity} units of {batch.medication.name} sold.',
				'data': {
					'medication': batch.medication.name,
					'quantity': quantity,
					'revenue': float(revenue),
					'remaining_stock': batch.quantity_remaining
				}
			})
			
		except Batch.DoesNotExist:
			return JsonResponse({
				'success': False,
				'message': 'Batch not found or inactive.'
			})
		except Exception as e:
			return JsonResponse({
				'success': False,
				'message': f'Error recording sale: {str(e)}'
			})
	
	return JsonResponse({
		'success': False,
		'message': 'Invalid request method.'
	})
