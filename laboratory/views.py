from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.permissions import (
    app_access_required, permission_required, lab_staff_required,
    can_edit_result, can_verify_result, can_delete_result, can_manage_lab,
    lab_verify_required, lab_manage_required, is_lab_staff,
)
from django.db.models import Q, Count, Max
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from .models import LabTest, LabTestRequest, LabTestResult, TestParameter, TestProfile, TestProfileParameter, ParameterResult, ParameterCategory, TestCategory
from .forms import LabTestForm, LabTestRequestForm, LabTestResultForm, TestParameterForm, TestProfileForm, ParameterResultInlineFormSet

@login_required
@app_access_required('laboratory')
def laboratory_dashboard(request):
	"""Laboratory dashboard with statistics and overview"""
	from patients.models import Patient
	
	today = timezone.now().date()
	
	# Statistics
	total_tests = LabTest.objects.filter(is_active=True).count()
	pending_requests = LabTestRequest.objects.filter(status__in=['requested', 'sample_collected', 'in_progress']).count()
	completed_today = LabTestRequest.objects.filter(status='completed', updated_at__date=today).count()
	urgent_tests = LabTestRequest.objects.filter(priority__in=['urgent', 'stat'], status__in=['requested', 'in_progress']).count()
	
	# Recent requests
	recent_requests = LabTestRequest.objects.select_related(
		'patient', 'test', 'requested_by'
	).order_by('-date_requested')[:10]
	
	# Pending results
	pending_results = LabTestRequest.objects.filter(
		status__in=['sample_collected', 'in_progress']
	).select_related('patient', 'test')[:10]
	
	# Tests by category
	tests_by_category = LabTest.objects.values('category').annotate(count=Count('id'))
	
	# Data for modals
	patients = Patient.objects.filter(is_active=True).order_by('first_name', 'last_name')
	available_tests = LabTest.objects.filter(is_active=True).order_by('category', 'name')
	pending_test_requests = LabTestRequest.objects.filter(
		status__in=['requested', 'sample_collected', 'in_progress']
	).select_related('patient', 'test').order_by('-date_requested')
	
	context = {
		'total_tests': total_tests,
		'pending_requests': pending_requests,
		'completed_today': completed_today,
		'urgent_tests': urgent_tests,
		'recent_requests': recent_requests,
		'pending_results': pending_results,
		'tests_by_category': tests_by_category,
		'patients': patients,
		'available_tests': available_tests,
		'pending_test_requests': pending_test_requests,
		'result_types': TestParameter.RESULT_TYPES,
		'flag_criteria': TestParameter.FLAG_CRITERIA,
	}
	return render(request, 'laboratory/dashboard.html', context)

@login_required
@app_access_required('laboratory')
def labtest_list(request):
	"""List all available laboratory tests"""
	category = request.GET.get('category', '')
	search = request.GET.get('search', '')
	
	tests = LabTest.objects.filter(is_active=True)
	
	if category:
		try:
			category_obj = TestCategory.objects.get(code=category)
			tests = tests.filter(category=category_obj)
		except TestCategory.DoesNotExist:
			tests = tests.none()
	
	if search:
		tests = tests.filter(
			Q(name__icontains=search) | 
			Q(code__icontains=search) | 
			Q(description__icontains=search)
		)
	
	categories = TestCategory.objects.filter(is_active=True)
	
	# Statistics (computed on all tests, not filtered)
	all_tests = LabTest.objects.all()
	total_tests = all_tests.count()
	active_tests = all_tests.filter(is_active=True).count()
	inactive_tests = all_tests.filter(is_active=False).count()
	
	# Tests by category
	tests_by_category = []
	for cat in categories:
		count = all_tests.filter(category=cat).count()
		if count > 0:
			tests_by_category.append({
				'category': cat.code,
				'code': cat.code,
				'label': cat.name,
				'count': count
			})
	
	# Quick info stats
	from django.db.models import Avg, Count
	profile_tests_count = all_tests.filter(profile__isnull=False).count()
	agg = all_tests.filter(is_active=True).aggregate(avg_price=Avg('price'), avg_tat=Avg('duration_hours'))
	avg_price = agg.get('avg_price')
	avg_tat = agg.get('avg_tat')
	
	# Most used tests (top 5 by request count)
	most_used_tests = LabTestRequest.objects.values('test', 'test__name').annotate(
		count=Count('id')
	).order_by('-count')[:5]
	
	# Total requests count
	total_requests = LabTestRequest.objects.count()
	
	context = {
		'tests': tests.select_related('category'),
		'categories': categories,
		'selected_category': category,
		'search_query': search,
		'result_types': TestParameter.RESULT_TYPES,
		'flag_criteria': TestParameter.FLAG_CRITERIA,
		# Stats
		'total_tests': total_tests,
		'active_tests': active_tests,
		'inactive_tests': inactive_tests,
		'tests_by_category': tests_by_category,
		'profile_tests_count': profile_tests_count,
		'avg_price': avg_price,
		'avg_tat': avg_tat,
		'most_used_tests': most_used_tests,
		'total_requests': total_requests,
	}
	return render(request, 'laboratory/labtest_list.html', context)

@login_required
@app_access_required('laboratory')
def labtest_detail(request, pk):
	"""View details of a specific laboratory test"""
	from datetime import timedelta, datetime
	from django.core.paginator import Paginator

	test = get_object_or_404(LabTest.objects.select_related('profile'), pk=pk)
	profile = test.profile
	parameters = []
	if profile:
		pps = TestProfileParameter.objects.filter(
			profile=profile
		).select_related('parameter').order_by('display_order', 'parameter__name')
		parameters = [pp.parameter for pp in pps]

	# Calculate time-based statistics
	now = timezone.now()
	today = now.date()
	week_start = today - timedelta(days=today.weekday())
	month_start = today.replace(day=1)
	
	daily_requests = test.requests.filter(date_requested__date=today).count()
	weekly_requests = test.requests.filter(date_requested__date__gte=week_start).count()
	monthly_requests = test.requests.filter(date_requested__date__gte=month_start).count()
	completed_requests = test.requests.filter(status='completed').count()

	# Requests & Results data (inline tab)
	test_requests = LabTestRequest.objects.filter(test=test).select_related(
		'patient', 'result'
	).order_by('-date_requested')

	# Apply filters
	rr_date_from = request.GET.get('date_from', '')
	rr_date_to = request.GET.get('date_to', '')
	rr_status = request.GET.get('rr_status', '')
	rr_patient = request.GET.get('rr_patient', '')

	if rr_date_from:
		try:
			test_requests = test_requests.filter(date_requested__date__gte=datetime.strptime(rr_date_from, '%Y-%m-%d').date())
		except ValueError:
			rr_date_from = ''
	if rr_date_to:
		try:
			test_requests = test_requests.filter(date_requested__date__lte=datetime.strptime(rr_date_to, '%Y-%m-%d').date())
		except ValueError:
			rr_date_to = ''
	if rr_status:
		test_requests = test_requests.filter(status=rr_status)
	if rr_patient:
		test_requests = test_requests.filter(
			Q(patient__first_name__icontains=rr_patient) |
			Q(patient__last_name__icontains=rr_patient) |
			Q(patient__patient_id__icontains=rr_patient)
		)

	rr_paginator = Paginator(test_requests, 25)
	rr_page = rr_paginator.get_page(request.GET.get('rr_page'))

	# Determine active tab
	active_tab = request.GET.get('tab', 'parameters')

	context = {
		'test': test,
		'profile': profile,
		'parameters': parameters,
		'result_types': TestParameter.RESULT_TYPES,
		'flag_criteria': TestParameter.FLAG_CRITERIA,
		'parameter_categories': ParameterCategory.objects.filter(is_active=True),
		'categories': TestCategory.objects.filter(is_active=True),
		'daily_requests': daily_requests,
		'weekly_requests': weekly_requests,
		'monthly_requests': monthly_requests,
		'completed_requests': completed_requests,
		# Requests & Results tab
		'rr_page_obj': rr_page,
		'rr_total': test.requests.count(),
		'rr_completed': completed_requests,
		'rr_date_from': rr_date_from,
		'rr_date_to': rr_date_to,
		'rr_status': rr_status,
		'rr_patient': rr_patient,
		'active_tab': active_tab,
	}
	return render(request, 'laboratory/labtest_detail.html', context)


@login_required
@app_access_required('laboratory')
def labtest_get_json(request, pk):
	"""Return test data as JSON for populating the edit modal"""
	import json as json_mod
	test = get_object_or_404(LabTest.objects.select_related('profile'), pk=pk)
	params = []
	if test.profile:
		pps = TestProfileParameter.objects.filter(
			profile=test.profile
		).select_related('parameter').order_by('display_order')
		for pp in pps:
			p = pp.parameter
			params.append({
				'name': p.name,
				'code': p.code,
				'category': p.category.code if p.category else 'chemical',
				'result_type': p.result_type,
				'unit': p.unit or '',
				'ref_min': float(p.reference_range_min) if p.reference_range_min is not None else '',
				'ref_max': float(p.reference_range_max) if p.reference_range_max is not None else '',
				'ref_text': p.reference_range_text or '',
				'flag_criteria': p.flag_criteria,
			})
	data = {
		'id': test.pk,
		'name': test.name,
		'code': test.code,
		'category': test.category.code if test.category else 'other',
		'description': test.description,
		'price': str(test.price),
		'currency': test.currency,
		'sample_type': test.sample_type,
		'duration_hours': test.duration_hours,
		'is_active': test.is_active,
		'parameters': params,
	}
	return JsonResponse(data)


@login_required
@lab_manage_required
def labtest_edit(request, pk):
	"""Edit an existing laboratory test and its inline parameters"""
	test = get_object_or_404(LabTest.objects.select_related('profile'), pk=pk)
	RESULT_TYPES = TestParameter.RESULT_TYPES
	FLAG_CRITERIA = TestParameter.FLAG_CRITERIA

	# Get existing parameters for pre-population
	existing_params = []
	if test.profile:
		pps = TestProfileParameter.objects.filter(
			profile=test.profile
		).select_related('parameter').order_by('display_order')
		for pp in pps:
			p = pp.parameter
			existing_params.append({
				'name': p.name,
				'code': p.code,
				'result_type': p.result_type,
				'unit': p.unit or '',
				'ref_min': p.reference_range_min if p.reference_range_min is not None else '',
				'ref_max': p.reference_range_max if p.reference_range_max is not None else '',
				'ref_text': p.reference_range_text or '',
				'flag_criteria': p.flag_criteria,
			})

	if request.method == 'POST':
		# Preprocess POST data to convert category code to ID
		post_data = request.POST.copy()
		if 'category' in post_data:
			category_value = post_data['category']
			# Check if it's a code (string) rather than an ID (integer)
			if not category_value.isdigit():
				try:
					category_obj = TestCategory.objects.get(code=category_value)
					post_data['category'] = str(category_obj.id)
				except TestCategory.DoesNotExist:
					pass  # Let form validation handle the error
		
		form = LabTestForm(post_data, instance=test)
		if form.is_valid():
			test = form.save(commit=False)

			# Update or create profile
			if test.profile:
				profile = test.profile
				profile.name = test.name
				profile.description = test.description
				profile.category = test.category
				profile.sample_type = test.sample_type
				profile.duration_hours = test.duration_hours
				profile.price = test.price
				profile.currency = test.currency
				profile.is_active = test.is_active
				profile.save()
			else:
				profile, _ = TestProfile.objects.get_or_create(
					code=test.code,
					defaults={
						'name': test.name,
						'description': test.description,
						'category': test.category,
						'sample_type': test.sample_type,
						'duration_hours': test.duration_hours,
						'price': test.price,
						'currency': test.currency,
						'is_active': test.is_active,
					}
				)
				test.profile = profile
			test.save()

			# Collect all submitted parameters first
			submitted_param_ids = set()
			i = 0
			while True:
				param_name = request.POST.get(f'param_{i}_name', '').strip()
				if not param_name:
					break
				param_code = request.POST.get(f'param_{i}_code', '').strip()
				param_category = request.POST.get(f'param_{i}_category', 'chemical')
				result_type = request.POST.get(f'param_{i}_result_type', 'numeric')
				unit = request.POST.get(f'param_{i}_unit', '').strip()
				ref_min = request.POST.get(f'param_{i}_ref_min', '').strip()
				ref_max = request.POST.get(f'param_{i}_ref_max', '').strip()
				ref_text = request.POST.get(f'param_{i}_ref_text', '').strip()
				flag_criteria = request.POST.get(f'param_{i}_flag_criteria', 'range')
				category_obj = ParameterCategory.objects.filter(code=param_category).first()

				if param_code:
					param, _ = TestParameter.objects.get_or_create(
						code=param_code,
						defaults={'name': param_name}
					)
					param.name = param_name
					param.category = category_obj
					param.result_type = result_type
					param.unit = unit
					param.flag_criteria = flag_criteria
					if ref_text:
						param.reference_range_text = ref_text
					try:
						param.reference_range_min = float(ref_min) if ref_min else None
						param.reference_range_max = float(ref_max) if ref_max else None
					except ValueError:
						pass
					param.display_order = i
					param.save()

					pp, created = TestProfileParameter.objects.get_or_create(
						profile=profile,
						parameter=param,
						defaults={'display_order': i}
					)
					if not created:
						pp.display_order = i
						pp.save(update_fields=['display_order'])
					submitted_param_ids.add(param.pk)
				i += 1

			# Only remove profile-parameter links that were explicitly removed by the user
			# (i.e. not in the submitted set), but keep them if no params were submitted
			# to avoid accidental wipe
			if submitted_param_ids:
				TestProfileParameter.objects.filter(
					profile=profile
				).exclude(
					parameter_id__in=submitted_param_ids
				).delete()

			messages.success(request, f'Laboratory test "{test.name}" updated with {i} parameter(s)!')
			if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
				return JsonResponse({'success': True, 'message': f'Laboratory test "{test.name}" updated successfully!'})
			return redirect('laboratory:labtest_detail', pk=test.pk)
		else:
			# Debug form errors
			print("Form errors:", form.errors)
			if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
				return JsonResponse({'success': False, 'errors': form.errors}, status=400)
	else:
		form = LabTestForm(instance=test)

	import json
	context = {
		'form': form,
		'test': test,
		'result_types': RESULT_TYPES,
		'flag_criteria': FLAG_CRITERIA,
		'existing_params_json': json.dumps(existing_params),
		'editing': True,
	}
	return render(request, 'laboratory/labtest_add.html', context)


@login_required
@lab_manage_required
def labtest_toggle_active(request, pk):
	"""Activate or deactivate a lab test via POST"""
	test = get_object_or_404(LabTest, pk=pk)
	if request.method == 'POST':
		test.is_active = not test.is_active
		test.save(update_fields=['is_active'])
		status_word = 'activated' if test.is_active else 'deactivated'
		if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
			return JsonResponse({'success': True, 'message': f'"{test.name}" {status_word}.', 'is_active': test.is_active})
		messages.success(request, f'"{test.name}" has been {status_word}.')
	return redirect('laboratory:labtest_list')


@login_required
@lab_manage_required
def labtest_add(request):
	"""Add a new laboratory test type with inline parameters"""
	RESULT_TYPES = TestParameter.RESULT_TYPES
	FLAG_CRITERIA = TestParameter.FLAG_CRITERIA
	
	if request.method == 'POST':
		form = LabTestForm(request.POST)
		if form.is_valid():
			test = form.save(commit=False)
			
			# Auto-create a profile for this test
			profile, _ = TestProfile.objects.get_or_create(
				code=test.code,
				defaults={
					'name': test.name,
					'description': test.description,
					'category': test.category,
					'sample_type': test.sample_type,
					'duration_hours': test.duration_hours,
					'price': test.price,
					'currency': test.currency,
					'is_active': test.is_active,
				}
			)
			test.profile = profile
			test.save()
			
			# Process inline parameters
			i = 0
			while True:
				param_name = request.POST.get(f'param_{i}_name', '').strip()
				if not param_name:
					break
				param_code = request.POST.get(f'param_{i}_code', '').strip()
				result_type = request.POST.get(f'param_{i}_result_type', 'numeric')
				unit = request.POST.get(f'param_{i}_unit', '').strip()
				ref_min = request.POST.get(f'param_{i}_ref_min', '').strip()
				ref_max = request.POST.get(f'param_{i}_ref_max', '').strip()
				ref_text = request.POST.get(f'param_{i}_ref_text', '').strip()
				flag_criteria = request.POST.get(f'param_{i}_flag_criteria', 'range')
				
				if param_code:
					param, _ = TestParameter.objects.get_or_create(
						code=param_code,
						defaults={'name': param_name}
					)
					param.name = param_name
					param.result_type = result_type
					param.unit = unit
					param.flag_criteria = flag_criteria
					if ref_text:
						param.reference_range_text = ref_text
					try:
						param.reference_range_min = float(ref_min) if ref_min else None
						param.reference_range_max = float(ref_max) if ref_max else None
					except ValueError:
						pass
					param.display_order = i
					param.save()
					
					TestProfileParameter.objects.get_or_create(
						profile=profile,
						parameter=param,
						defaults={'display_order': i}
					)
				i += 1
			
			messages.success(request, f'Laboratory test "{test.name}" added with {i} parameter(s)!')
			if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
				return JsonResponse({'success': True, 'message': f'Laboratory test "{test.name}" added successfully!'})
			return redirect('laboratory:labtest_list')
		else:
			if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
				return JsonResponse({'success': False, 'errors': form.errors}, status=400)
		
	else:
		form = LabTestForm()
	
	context = {
		'form': form,
		'result_types': RESULT_TYPES,
		'flag_criteria': FLAG_CRITERIA,
	}
	return render(request, 'laboratory/labtest_add.html', context)

@login_required
@permission_required('laboratory', 'create')
def labtest_request_bulk(request):
	"""Request multiple laboratory tests for a patient in one go - AJAX only"""
	if request.method != 'POST':
		return JsonResponse({'success': False, 'message': 'POST required'}, status=405)

	from billing.models import Invoice, InvoiceLineItem
	from .models import LabTestPriceGroup
	from billing.signals import generate_invoice_number
	from datetime import timedelta
	from decimal import Decimal

	patient_id = request.POST.get('patient', '')
	test_ids = request.POST.getlist('tests')  # multiple test IDs
	priority = request.POST.get('priority', 'routine')
	reason_for_test = request.POST.get('reason_for_test', '')
	samples_required = request.POST.get('samples_required', '')
	clinical_notes = request.POST.get('clinical_notes', '')
	sample_id = request.POST.get('sample_id', '')
	override_group_id = request.POST.get('override_group_id', '').strip()
	discount_type = request.POST.get('discount_type', 'none')
	discount_scope = request.POST.get('discount_scope', 'all')  # 'all' or 'single'
	discount_test_id = request.POST.get('discount_test_id', '').strip()
	try:
		discount_value = Decimal(request.POST.get('discount_value', '0') or '0')
	except Exception:
		discount_value = Decimal('0')

	if not patient_id or not test_ids:
		return JsonResponse({'success': False, 'message': 'Patient and at least one test are required.'}, status=400)

	from patients.models import Patient
	try:
		patient = Patient.objects.get(id=patient_id)
	except Patient.DoesNotExist:
		return JsonResponse({'success': False, 'message': 'Patient not found.'}, status=404)

	# Get or create draft invoice
	draft_invoice = Invoice.objects.filter(patient=patient, status='draft').first()
	if not draft_invoice:
		draft_invoice = Invoice.objects.create(
			invoice_number=generate_invoice_number(),
			patient=patient,
			due_date=timezone.now().date() + timedelta(days=30),
			status='draft',
			created_by=request.user
		)

	# --- Pass 1: resolve base prices for all requested tests ---
	test_data = []  # list of (lab_test, base_price)
	for test_id in test_ids:
		try:
			lab_test = LabTest.objects.get(id=test_id, is_active=True)
		except LabTest.DoesNotExist:
			continue
		if override_group_id:
			try:
				gp = LabTestPriceGroup.objects.get(lab_test=lab_test, patient_group_id=override_group_id)
				base = gp.price
			except LabTestPriceGroup.DoesNotExist:
				base = lab_test.price
		else:
			base = LabTestPriceGroup.get_price_for_patient(lab_test, patient)
		test_data.append((lab_test, base))

	if not test_data:
		return JsonResponse({'success': False, 'message': 'No valid tests were found.'}, status=400)

	# --- Compute total discount amount (applied to whole order for scope=all) ---
	total_base = sum(bp for _, bp in test_data)
	total_disc = Decimal('0')
	if discount_type != 'none' and discount_value > Decimal('0'):
		if discount_scope == 'all':
			if discount_type == 'percentage' and discount_value <= Decimal('100'):
				total_disc = (total_base * discount_value / 100).quantize(Decimal('0.01'))
			elif discount_type == 'flat':
				total_disc = min(discount_value, total_base)
		elif discount_scope == 'single' and discount_test_id:
			for lt, bp in test_data:
				if str(lt.id) == discount_test_id:
					if discount_type == 'percentage' and discount_value <= Decimal('100'):
						total_disc = (bp * discount_value / 100).quantize(Decimal('0.01'))
					elif discount_type == 'flat':
						total_disc = min(discount_value, bp)
					break

	# --- Pass 2: create requests and invoice line items ---
	created_count = 0
	disc_assigned = Decimal('0')
	for idx, (lab_test, base_price) in enumerate(test_data):
		lab_request = LabTestRequest.objects.create(
			patient=patient,
			test=lab_test,
			requested_by=request.user,
			priority=priority,
			reason_for_test=reason_for_test,
			samples_required=samples_required,
			clinical_notes=clinical_notes,
			sample_id=sample_id,
		)

		row_disc = Decimal('0')
		if total_disc > Decimal('0'):
			if discount_scope == 'all':
				# distribute proportionally; last item gets remainder
				if idx == len(test_data) - 1:
					row_disc = total_disc - disc_assigned
				elif total_base > Decimal('0'):
					row_disc = (total_disc * base_price / total_base).quantize(Decimal('0.01'))
				disc_assigned += row_disc
			elif discount_scope == 'single' and str(lab_test.id) == discount_test_id:
				row_disc = total_disc

		unit_price = max(Decimal('0'), base_price - row_disc)

		InvoiceLineItem.objects.create(
			invoice=draft_invoice,
			lab_test_request=lab_request,
			description=f"Lab Test: {lab_test.name}",
			quantity=1,
			unit_price=unit_price,
			total_amount=unit_price,
		)
		created_count += 1

	if created_count == 0:
		return JsonResponse({'success': False, 'message': 'No valid tests were found.'}, status=400)

	return JsonResponse({
		'success': True,
		'message': f'{created_count} lab test(s) requested and added to invoice successfully!'
	})


@login_required
@permission_required('laboratory', 'create')
def labtest_request(request):
	"""Request a laboratory test for a patient - AJAX/Modal only"""
	# Redirect GET requests to request list page
	if request.method != 'POST':
		messages.info(request, 'Please use the "New Request" button to create a lab test request.')
		return redirect('laboratory:request_list')
	
	form = LabTestRequestForm(request.POST)
	if form.is_valid():
		lab_request = form.save(commit=False)
		lab_request.requested_by = request.user
		lab_request.save()
		
		# Automatically create invoice for the lab test
		from billing.models import Invoice, InvoiceLineItem
		from .models import LabTestPriceGroup
		from datetime import timedelta
		from django.utils import timezone
		
		patient = lab_request.patient
		lab_test = lab_request.test
		
		# Get base price — respect override group or patient's group
		from decimal import Decimal
		override_group_id = request.POST.get('override_group_id', '').strip()
		discount_type = request.POST.get('discount_type', 'none')
		try:
			discount_value = Decimal(request.POST.get('discount_value', '0') or '0')
		except Exception:
			discount_value = Decimal('0')

		if override_group_id:
			try:
				group_price_entry = LabTestPriceGroup.objects.get(lab_test=lab_test, patient_group_id=override_group_id)
				unit_price = group_price_entry.price
			except LabTestPriceGroup.DoesNotExist:
				unit_price = lab_test.price
		else:
			unit_price = LabTestPriceGroup.get_price_for_patient(lab_test, patient)

		# Apply discount
		if discount_type == 'percentage' and Decimal('0') < discount_value <= Decimal('100'):
			unit_price = (unit_price * (1 - discount_value / 100)).quantize(Decimal('0.01'))
		elif discount_type == 'flat' and discount_value > Decimal('0'):
			unit_price = max(Decimal('0'), unit_price - discount_value)

		# Check if patient has an open draft invoice
		draft_invoice = Invoice.objects.filter(
			patient=patient,
			status='draft'
		).first()
		
		if not draft_invoice:
			# Create new invoice
			from billing.signals import generate_invoice_number
			invoice_number = generate_invoice_number()
			draft_invoice = Invoice.objects.create(
				invoice_number=invoice_number,
				patient=patient,
				due_date=timezone.now().date() + timedelta(days=30),
				status='draft',
				created_by=request.user
			)
		
		# Add lab test as line item
		InvoiceLineItem.objects.create(
			invoice=draft_invoice,
			lab_test_request=lab_request,
			description=f"Lab Test: {lab_test.name}",
			quantity=1,
			unit_price=unit_price,
			total_amount=unit_price
		)
		
		# Check if AJAX request
		if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
			return JsonResponse({
				'success': True,
				'message': 'Laboratory test requested and added to invoice successfully!'
			})
		messages.success(request, 'Laboratory test requested and added to invoice successfully!')
		return redirect('laboratory:request_list')
	else:
		# Return errors for AJAX
		if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
			return JsonResponse({
				'success': False,
				'errors': form.errors
			}, status=400)
		# For non-AJAX POST with errors, redirect with error message
		messages.error(request, 'Error creating lab test request. Please try again.')
		return redirect('laboratory:request_list')


@login_required
@app_access_required('laboratory')
def get_price_preview(request):
	"""AJAX: return base/final price for a test+patient+group+discount combo"""
	from decimal import Decimal
	from patients.models import Patient, PatientGroup
	from .models import LabTestPriceGroup

	test_id = request.GET.get('test_id', '').strip()
	patient_id = request.GET.get('patient_id', '').strip()
	override_group_id = request.GET.get('override_group_id', '').strip()
	discount_type = request.GET.get('discount_type', 'none')
	try:
		discount_value = Decimal(request.GET.get('discount_value', '0') or '0')
	except Exception:
		discount_value = Decimal('0')

	if not test_id:
		return JsonResponse({'success': False, 'message': 'test_id required'}, status=400)

	try:
		lab_test = LabTest.objects.get(pk=test_id)
	except (LabTest.DoesNotExist, ValueError):
		return JsonResponse({'success': False, 'message': 'Test not found'}, status=404)

	patient = None
	patient_group_id = ''
	patient_group_name = ''
	if patient_id:
		try:
			patient = Patient.objects.select_related('patient_group').get(pk=patient_id)
			if patient.patient_group:
				patient_group_id = patient.patient_group_id
				patient_group_name = patient.patient_group.name
		except (Patient.DoesNotExist, ValueError):
			pass

	# Resolve base price
	if override_group_id:
		try:
			entry = LabTestPriceGroup.objects.get(lab_test=lab_test, patient_group_id=override_group_id)
			base_price = entry.price
		except LabTestPriceGroup.DoesNotExist:
			base_price = lab_test.price
	elif patient:
		base_price = LabTestPriceGroup.get_price_for_patient(lab_test, patient)
	else:
		base_price = lab_test.price

	# Apply discount
	discount_amount = Decimal('0')
	final_price = base_price
	if discount_type == 'percentage' and Decimal('0') < discount_value <= Decimal('100'):
		discount_amount = (base_price * discount_value / 100).quantize(Decimal('0.01'))
		final_price = base_price - discount_amount
	elif discount_type == 'flat' and discount_value > Decimal('0'):
		discount_amount = min(discount_value, base_price)
		final_price = max(Decimal('0'), base_price - discount_amount)

	# All group prices for this test (for the group selector hint)
	group_prices = {
		str(gp.patient_group_id): float(gp.price)
		for gp in LabTestPriceGroup.objects.filter(lab_test=lab_test).select_related('patient_group')
	}

	return JsonResponse({
		'success': True,
		'default_price': float(lab_test.price),
		'base_price': float(base_price),
		'discount_amount': float(discount_amount),
		'final_price': float(final_price),
		'currency': lab_test.currency,
		'patient_group_id': patient_group_id,
		'patient_group_name': patient_group_name,
		'group_prices': group_prices,
	})


@login_required
@app_access_required('laboratory')
def request_list(request):
	"""List all laboratory test requests"""
	from datetime import timedelta, date, datetime

	status = request.GET.get('status', '')
	priority = request.GET.get('priority', '')
	search = request.GET.get('search', '')
	date_range = request.GET.get('date_range', '')
	date_from = request.GET.get('date_from', '')
	date_to = request.GET.get('date_to', '')
	has_results = request.GET.get('has_results', '')
	
	requests_qs = LabTestRequest.objects.select_related(
		'patient', 'test', 'test__category', 'requested_by'
	).order_by('-date_requested')
	
	# Apply filters
	if status:
		requests_qs = requests_qs.filter(status=status)
	
	if priority:
		requests_qs = requests_qs.filter(priority=priority)
	
	if search:
		requests_qs = requests_qs.filter(
			Q(patient__first_name__icontains=search) |
			Q(patient__last_name__icontains=search) |
			Q(patient__patient_id__icontains=search) |
			Q(test__name__icontains=search) |
			Q(test__code__icontains=search) |
			Q(id__icontains=search)
		)
	
	# Date filtering
	if date_range == 'today':
		today = timezone.now().date()
		requests_qs = requests_qs.filter(date_requested__date=today)
	elif date_range == 'week':
		start_of_week = timezone.now().date() - timedelta(days=timezone.now().date().weekday())
		requests_qs = requests_qs.filter(date_requested__date__gte=start_of_week)
	elif date_range == 'month':
		start_of_month = timezone.now().date().replace(day=1)
		requests_qs = requests_qs.filter(date_requested__date__gte=start_of_month)
	elif date_range == 'custom' and date_from:
		try:
			date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
			requests_qs = requests_qs.filter(date_requested__date__gte=date_from_obj)
			if date_to:
				date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
				requests_qs = requests_qs.filter(date_requested__date__lte=date_to_obj)
		except ValueError:
			pass
	
	# Results filtering
	if has_results == 'yes':
		requests_qs = requests_qs.filter(result__isnull=False)
	elif has_results == 'no':
		requests_qs = requests_qs.filter(result__isnull=True)

	# --- Statistics (always computed on ALL requests, unfiltered) ---
	now = timezone.now()
	all_requests = LabTestRequest.objects.all()
	total_all = all_requests.count()

	# Time-based counts
	start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
	start_of_week = start_of_today - timedelta(days=start_of_today.weekday())  # Monday
	start_of_month = start_of_today.replace(day=1)

	today_count = all_requests.filter(date_requested__gte=start_of_today).count()
	week_count = all_requests.filter(date_requested__gte=start_of_week).count()
	month_count = all_requests.filter(date_requested__gte=start_of_month).count()

	# Result-based counts
	with_results = all_requests.filter(result__isnull=False).count()
	pending = all_requests.filter(result__isnull=True).exclude(status='cancelled').count()
	completed = all_requests.filter(status='completed').count()
	cancelled = all_requests.filter(status='cancelled').count()
	in_progress = all_requests.filter(status='in_progress').count()
	
	# Priority-based counts
	stat_count = all_requests.filter(priority='stat').count()
	urgent_count = all_requests.filter(priority='urgent').count()
	high_count = all_requests.filter(priority='high').count()
	normal_count = all_requests.filter(priority='normal').count()

	# Get data for modal
	from patients.models import Patient, PatientGroup
	patients = Patient.objects.filter(is_active=True).select_related('patient_group').order_by('first_name', 'last_name')
	lab_tests = LabTest.objects.filter(is_active=True).order_by('name')
	patient_groups = PatientGroup.objects.filter(is_active=True).order_by('name')
	
	context = {
		'requests': requests_qs,
		'status_choices': LabTestRequest.STATUS_CHOICES,
		'priority_choices': LabTestRequest.PRIORITY_CHOICES,
		'selected_status': status,
		'selected_priority': priority,
		# Stats
		'total_all': total_all,
		'today_count': today_count,
		'week_count': week_count,
		'month_count': month_count,
		'with_results': with_results,
		'pending': pending,
		'completed': completed,
		'cancelled': cancelled,
		'in_progress': in_progress,
		# Priority stats
		'stat_count': stat_count,
		'urgent_count': urgent_count,
		'high_count': high_count,
		'normal_count': normal_count,
		# Modal data
		'patients': patients,
		'lab_tests': lab_tests,
		'patient_groups': patient_groups,
	}
	return render(request, 'laboratory/request_list.html', context)

@login_required
@app_access_required('laboratory')
def export_requests(request):
	"""Export laboratory requests to CSV"""
	import csv
	from datetime import datetime
	from django.http import HttpResponse
	
	# Get the same filters as request_list
	status = request.GET.get('status', '')
	priority = request.GET.get('priority', '')
	search = request.GET.get('search', '')
	date_range = request.GET.get('date_range', '')
	date_from = request.GET.get('date_from', '')
	date_to = request.GET.get('date_to', '')
	has_results = request.GET.get('has_results', '')
	
	requests_qs = LabTestRequest.objects.select_related(
		'patient', 'test', 'test__category', 'requested_by'
	).order_by('-date_requested')
	
	# Apply the same filters
	if status:
		requests_qs = requests_qs.filter(status=status)
	if priority:
		requests_qs = requests_qs.filter(priority=priority)
	if search:
		requests_qs = requests_qs.filter(
			Q(patient__first_name__icontains=search) |
			Q(patient__last_name__icontains=search) |
			Q(patient__patient_id__icontains=search) |
			Q(test__name__icontains=search) |
			Q(test__code__icontains=search) |
			Q(id__icontains=search)
		)
	if date_range == 'today':
		today = timezone.now().date()
		requests_qs = requests_qs.filter(date_requested__date=today)
	elif date_range == 'week':
		start_of_week = timezone.now().date() - timedelta(days=timezone.now().date().weekday())
		requests_qs = requests_qs.filter(date_requested__date__gte=start_of_week)
	elif date_range == 'month':
		start_of_month = timezone.now().date().replace(day=1)
		requests_qs = requests_qs.filter(date_requested__date__gte=start_of_month)
	elif date_range == 'custom' and date_from:
		try:
			date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
			requests_qs = requests_qs.filter(date_requested__date__gte=date_from_obj)
			if date_to:
				date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
				requests_qs = requests_qs.filter(date_requested__date__lte=date_to_obj)
		except ValueError:
			pass
	if has_results == 'yes':
		requests_qs = requests_qs.filter(result__isnull=False)
	elif has_results == 'no':
		requests_qs = requests_qs.filter(result__isnull=True)
	
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = f'attachment; filename="lab_requests_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
	
	writer = csv.writer(response)
	writer.writerow([
		'Request ID', 'Patient ID', 'Patient Name', 'Test Name', 'Test Code', 
		'Category', 'Status', 'Priority', 'Date Requested', 'Requested By',
		'Has Results', 'Result Date'
	])
	
	for req in requests_qs:
		writer.writerow([
			f'REQ-{req.id:05d}',
			req.patient.patient_id,
			req.patient.get_full_name(),
			req.test.name,
			req.test.code,
			req.test.category.name if req.test.category else '',
			req.get_status_display(),
			req.get_priority_display(),
			req.date_requested.strftime('%Y-%m-%d %H:%M'),
			req.requested_by.get_full_name() if req.requested_by else '',
			'Yes' if req.result else 'No',
			req.result.created_at.strftime('%Y-%m-%d %H:%M') if req.result else ''
		])
	
	return response

@login_required
@app_access_required('laboratory')
def request_detail(request, pk):
	"""View details of a specific test request"""
	lab_request = get_object_or_404(
		LabTestRequest.objects.select_related(
			'patient', 'test', 'test__profile', 'requested_by'
		),
		pk=pk
	)
	
	try:
		result = lab_request.result
	except LabTestResult.DoesNotExist:
		result = None
	
	# Get profile parameters if test has a profile
	profile = lab_request.test.profile if lab_request.test.profile_id else None
	profile_parameters = []
	
	# Build a dict of parameter_id → ParameterResult for easy lookup
	param_results_map = {}
	if result:
		for pr in result.parameter_results.select_related('parameter').all():
			param_results_map[pr.parameter_id] = pr
	
	if profile:
		pps = TestProfileParameter.objects.filter(
			profile=profile
		).select_related('parameter').order_by('display_order', 'parameter__name')
		
		# Combine into list of (TestProfileParameter, ParameterResult|None)
		seen_param_ids = set()
		for pp in pps:
			pr = param_results_map.get(pp.parameter_id)
			profile_parameters.append({'pp': pp, 'param': pp.parameter, 'pr': pr})
			seen_param_ids.add(pp.parameter_id)
		
		# Also include any saved ParameterResults whose parameters are NOT in the current profile
		for param_id, pr in param_results_map.items():
			if param_id not in seen_param_ids:
				profile_parameters.append({'pp': None, 'param': pr.parameter, 'pr': pr})
	elif param_results_map:
		# No profile but there are saved parameter results — show them all
		for param_id, pr in param_results_map.items():
			profile_parameters.append({'pp': None, 'param': pr.parameter, 'pr': pr})
	
	# Permission flags for template
	user_can_edit = can_edit_result(request.user, result) if result else False
	user_can_verify = can_verify_result(request.user)

	context = {
		'request': lab_request,
		'result': result,
		'profile': profile,
		'profile_parameters': profile_parameters,
		'can_edit_result': user_can_edit,
		'can_verify_result': user_can_verify,
	}
	return render(request, 'laboratory/request_detail.html', context)

@login_required
@app_access_required('laboratory')
def labtest_results(request):
	"""List all laboratory test results"""
	results = LabTestResult.objects.select_related(
		'request', 'request__patient', 'request__test', 'reported_by', 'verified_by'
	).order_by('-date_reported')
	
	# Get pending test requests (those without results)
	pending_requests = LabTestRequest.objects.filter(
		status__in=['requested', 'sample_collected', 'in_progress']
	).select_related('patient', 'test').order_by('-date_requested')
	
	context = {
		'results': results,
		'pending_requests': pending_requests
	}
	return render(request, 'laboratory/labtest_results.html', context)

@login_required
@permission_required('laboratory', 'create')
def labtest_result_add(request, request_id=None):
	"""Add result for a laboratory test request"""
	lab_request = None
	if request_id:
		lab_request = get_object_or_404(LabTestRequest, pk=request_id)
	
	if request.method == 'POST':
		form = LabTestResultForm(request.POST)
		if form.is_valid():
			result = form.save(commit=False)
			result.reported_by = request.user
			result.save()
			
			# Update request status
			result.request.status = 'completed'
			result.request.save()
			
			# Check if AJAX request
			if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
				return JsonResponse({
					'success': True,
					'message': 'Laboratory result added successfully!',
					'redirect': f'/laboratory/requests/{result.request.pk}/'
				})
			messages.success(request, 'Laboratory result added successfully!')
			return redirect('laboratory:request_detail', pk=result.request.pk)
		else:
			# Return errors for AJAX
			if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
				return JsonResponse({
					'success': False,
					'errors': form.errors
				}, status=400)
	else:
		initial = {}
		if lab_request:
			initial['request'] = lab_request
		form = LabTestResultForm(initial=initial)
	
	context = {
		'form': form,
		'lab_request': lab_request,
	}
	return render(request, 'laboratory/labtest_result_add.html', context)

@login_required
@permission_required('laboratory', 'create')
def add_result_modal(request, request_id):
	"""AJAX view: create LabTestResult + per-parameter ParameterResults from modal form"""
	lab_request = get_object_or_404(
		LabTestRequest.objects.select_related('test', 'test__profile'),
		pk=request_id
	)
	
	# Guard: already has a result
	if hasattr(lab_request, 'result'):
		return JsonResponse({'success': False, 'message': 'A result already exists for this request.'}, status=400)
	
	if request.method != 'POST':
		return JsonResponse({'success': False, 'message': 'POST required.'}, status=405)
	
	# Collect summary fields
	overall_value  = request.POST.get('overall_value', '').strip()
	interpretation = request.POST.get('interpretation', '').strip()
	remarks        = request.POST.get('remarks', '').strip()
	is_abnormal    = request.POST.get('is_abnormal') == '1'
	
	# Update patient vitals if provided
	height = request.POST.get('height', '').strip()
	weight = request.POST.get('weight', '').strip()
	bmi = request.POST.get('bmi', '').strip()
	
	if height or weight or bmi:
		patient = lab_request.patient
		if height:
			try:
				patient.height = float(height)
			except (ValueError, TypeError):
				pass
		if weight:
			try:
				patient.weight = float(weight)
			except (ValueError, TypeError):
				pass
		if bmi:
			try:
				patient.bmi = float(bmi)
			except (ValueError, TypeError):
				pass
		patient.save(update_fields=['height', 'weight', 'bmi'])
	
	# Build LabTestResult
	result = LabTestResult(
		request=lab_request,
		result_value=overall_value or '—',
		interpretation=interpretation,
		remarks=remarks,
		is_abnormal=is_abnormal,
		reported_by=request.user,
	)
	result.save()
	
	# Process per-parameter values
	profile = lab_request.test.profile
	if profile:
		pps = TestProfileParameter.objects.filter(
			profile=profile
		).select_related('parameter').order_by('display_order', 'parameter__name')
		
		any_abnormal = False
		for i, pp in enumerate(pps):
			val = request.POST.get(f'param_{pp.parameter_id}', '').strip()
			if not val:
				continue
			pr = ParameterResult(
				test_result=result,
				parameter=pp.parameter,
				result_value=val,
				notes=request.POST.get(f'param_{pp.parameter_id}_notes', '').strip(),
			)
			pr.save()  # auto-evaluates flag via model save()
			if pr.flag in ('low', 'high', 'critical_low', 'critical_high', 'abnormal'):
				any_abnormal = True
		
		# Update overall is_abnormal based on parameter flags
		if any_abnormal and not is_abnormal:
			result.is_abnormal = True
			result.save(update_fields=['is_abnormal'])
	
	# Mark request as completed
	lab_request.status = 'completed'
	lab_request.save(update_fields=['status'])
	
	return JsonResponse({
		'success': True,
		'message': f'Results recorded for {lab_request.test.name}.',
	})


@login_required
@permission_required('laboratory', 'create')
def update_request_status(request, pk):
    """Update lab request status via AJAX"""
    if request.method == 'POST':
        lab_request = get_object_or_404(LabTestRequest, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(LabTestRequest.STATUS_CHOICES):
            lab_request.status = new_status
            if new_status == 'sample_collected':
                lab_request.sample_collected_at = timezone.now()
            lab_request.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Status updated successfully'})
            messages.success(request, 'Lab request status updated.')
            return redirect('laboratory:request_detail', pk=pk)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Invalid status'}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

@login_required
@app_access_required('laboratory')
def request_print(request, pk):
	"""Printable version of a lab test request — supports multiple IDs via ?ids=1,2,3"""
	from clinic_settings.models import ClinicSettings
	import qrcode
	from io import BytesIO
	import base64
	
	# Check for multi-select IDs in query string
	ids_param = request.GET.get('ids', '')
	if ids_param:
		try:
			pk_list = [int(x) for x in ids_param.split(',') if x.strip()]
		except ValueError:
			pk_list = [pk]
	else:
		pk_list = [pk]
	
	lab_requests = list(
		LabTestRequest.objects.filter(pk__in=pk_list).select_related('patient', 'test', 'requested_by')
	)
	if not lab_requests:
		from django.http import Http404
		raise Http404("No lab requests found.")
	
	# Build list of request data with results
	lab_request_data = []
	for lr in lab_requests:
		try:
			result = lr.result
		except LabTestResult.DoesNotExist:
			result = None
		lab_request_data.append({
			'request_obj': lr,
			'test': lr.test,
			'result': result,
		})
	
	primary_request = lab_requests[0]
	
	try:
		clinic_settings = ClinicSettings.objects.first()
	except:
		clinic_settings = None
	
	# Generate QR code for request verification
	request_url = request.build_absolute_uri()
	qr = qrcode.QRCode(version=1, box_size=10, border=2)
	qr.add_data(request_url)
	qr.make(fit=True)
	qr_img = qr.make_image(fill_color="black", back_color="white")
	
	# Convert QR code to base64 for embedding in HTML
	buffer = BytesIO()
	qr_img.save(buffer, format='PNG')
	qr_base64 = base64.b64encode(buffer.getvalue()).decode()
	
	context = {
		'request': primary_request,
		'clinic_settings': clinic_settings,
		'lab_requests': lab_requests,
		'lab_request_data': lab_request_data,
		'multi_test': len(lab_request_data) > 1,
		'qr_code': qr_base64,
	}
	return render(request, 'laboratory/request_print.html', context)

@login_required
@app_access_required('laboratory')
def test_report(request, pk):
	"""Printable lab test results report — supports multiple IDs via ?ids=1,2,3
	   Groups tests by category when more than one category is present."""
	from clinic_settings.models import ClinicSettings
	from collections import OrderedDict
	import qrcode
	from io import BytesIO
	import base64

	# ── Support multi-test via ?ids= query param ──
	ids_param = request.GET.get('ids', '')
	if ids_param:
		try:
			pk_list = [int(x) for x in ids_param.split(',') if x.strip()]
		except ValueError:
			pk_list = [pk]
	else:
		pk_list = [pk]

	lab_requests = list(
		LabTestRequest.objects.filter(pk__in=pk_list)
		.select_related('patient', 'test', 'test__profile', 'requested_by')
		.order_by('test__category', 'pk')
	)
	if not lab_requests:
		from django.http import Http404
		raise Http404("No lab requests found.")

	# Use the first request as the primary (for patient info, QR, etc.)
	lab_request = lab_requests[0]

	# Parse sections from URL
	sections_param = request.GET.get('sections', None)
	if sections_param is None:
		selected_sections = ['patient', 'results']
	else:
		selected_sections = [s.strip() for s in sections_param.split(',') if s.strip()]

	# ── Build category sections ──
	from django.db.models import Case, When, IntegerField
	category_order_expr = Case(
		When(parameter__category__code='physical', then=1),
		When(parameter__category__code='chemical', then=2),
		When(parameter__category__code='microscopic', then=3),
		default=4,
		output_field=IntegerField()
	)

	category_sections = OrderedDict()
	all_profile_parameters = []  # flat list for backward compat
	group_counter = 0

	for lr in lab_requests:
		try:
			lr_result = lr.result
		except LabTestResult.DoesNotExist:
			lr_result = None

		# Per-test parameter filter
		param_key = f'test_{lr.pk}_params'
		param_val = request.GET.get(param_key, '')
		allowed_params = [int(p) for p in param_val.split(',') if p.strip().isdigit()] if param_val else []

		profile_parameters = []
		if lr.test.profile:
			pps = TestProfileParameter.objects.filter(
				profile=lr.test.profile
			).select_related('parameter').order_by(category_order_expr, 'display_order', 'parameter__name')

			param_results_map = {}
			if lr_result:
				for pr in lr_result.parameter_results.select_related('parameter').all():
					param_results_map[pr.parameter_id] = pr

			for pp in pps:
				if not allowed_params or pp.parameter_id in allowed_params:
					pr = param_results_map.get(pp.parameter_id)
					profile_parameters.append({'param': pp.parameter, 'pr': pr})

		# Check if this test has any parameter categories (e.g. urinalysis: physical/chemical/microscopic)
		param_cats = set(item['param'].category.id for item in profile_parameters if item['param'].category)
		has_multiple_param_cats = len(param_cats) >= 1

		group_counter += 1
		cat = lr.test.category
		cat_display = lr.test.category.name if lr.test.category else 'Other'
		cat_key = cat.id if cat else 'other'
		if cat_key not in category_sections:
			category_sections[cat_key] = {
				'category': cat,
				'category_display': cat_display,
				'tests': [],
			}
		category_sections[cat_key]['tests'].append({
			'request_obj': lr,
			'test': lr.test,
			'result': lr_result,
			'profile_parameters': profile_parameters,
			'group_id': group_counter,
			'has_multiple_param_cats': has_multiple_param_cats,
		})
		all_profile_parameters.extend(profile_parameters)

	# Primary result for backward-compat context vars
	try:
		result = lab_request.result
	except LabTestResult.DoesNotExist:
		result = None

	try:
		clinic_settings = ClinicSettings.objects.first()
	except:
		clinic_settings = None

	# Build R2 public URL for QR code (same pattern as publish view)
	import re
	from django.conf import settings as _settings
	patient_name_raw = getattr(lab_request.patient, 'get_full_name', lambda: str(lab_request.patient))()
	if not patient_name_raw:
		patient_name_raw = str(lab_request.patient)
	safe_name = re.sub(r'[^\w]', '_', patient_name_raw).strip('_') or f'Patient_{pk}'
	r2_public = getattr(_settings, 'R2_PUBLIC_URL', '').rstrip('/')
	r2_qr_url = f'{r2_public}/reports/{safe_name}_report_{pk}.pdf' if r2_public else ''

	qr_url = (r2_qr_url or lab_request.report_gdrive_url or lab_request.report_pdf_url
	          or request.build_absolute_uri(request.path))
	qr = qrcode.QRCode(version=1, box_size=10, border=2)
	qr.add_data(qr_url)
	qr.make(fit=True)
	qr_img = qr.make_image(fill_color="black", back_color="white")
	buffer = BytesIO()
	qr_img.save(buffer, format='PNG')
	qr_base64 = base64.b64encode(buffer.getvalue()).decode()

	comment = request.GET.get('comment', '')

	# Report type & referring doctor info
	report_type = request.GET.get('report_type', 'final')
	ref_doctor = request.GET.get('ref_doctor', '')
	ref_location = request.GET.get('ref_location', '')
	ref_contact = request.GET.get('ref_contact', '')

	# Sample type from the primary test
	sample_type = lab_request.test.sample_type or (lab_request.test.profile.sample_type if lab_request.test.profile else '') or ''

	# Parse patient_fields for selective display
	patient_fields_param = request.GET.get('patient_fields', '')
	if patient_fields_param:
		patient_fields = [s.strip() for s in patient_fields_param.split(',') if s.strip()]
	else:
		patient_fields = [
			'patient_name', 'patient_id', 'age', 'gender', 'dob', 'phone',
			'nationality', 'id_type', 'id_number', 'test_date', 'referring_doctor',
			'reason_for_test', 'clinical_notes',
		]

	context = {
		'request': lab_request,
		'result': result,
		'profile_parameters': all_profile_parameters,  # backward compat
		'category_sections': list(category_sections.values()),
		'multi_category': len(category_sections) > 1,
		'clinic_settings': clinic_settings,
		'qr_code': qr_base64,
		'cloud_url': lab_request.report_pdf_url,
		'gdrive_url': lab_request.report_gdrive_url,
		'comment': comment,
		'report_type': report_type,
		'ref_doctor': ref_doctor,
		'ref_location': ref_location,
		'ref_contact': ref_contact,
		'sample_type': sample_type,
		'show_patient': 'patient' in selected_sections,
		'show_results': 'results' in selected_sections,
		# Patient info sub-fields
		'show_patient_name': 'patient_name' in patient_fields,
		'show_patient_id': 'patient_id' in patient_fields,
		'show_age': 'age' in patient_fields,
		'show_gender': 'gender' in patient_fields,
		'show_dob': 'dob' in patient_fields,
		'show_phone': 'phone' in patient_fields,
		'show_nationality': 'nationality' in patient_fields,
		'show_id_type': 'id_type' in patient_fields,
		'show_id_number': 'id_number' in patient_fields,
		'show_test_date': 'test_date' in patient_fields,
		'show_referring_doctor': 'referring_doctor' in patient_fields,
		'show_reason_for_test': 'reason_for_test' in patient_fields,
		'show_clinical_notes': 'clinical_notes' in patient_fields,
	}
	return render(request, 'laboratory/test_report.html', context)

@login_required
@lab_staff_required
def edit_result_modal(request, request_id):
	"""AJAX view: edit existing LabTestResult + per-parameter ParameterResults"""
	lab_request = get_object_or_404(
		LabTestRequest.objects.select_related('test', 'test__profile'),
		pk=request_id
	)

	try:
		result = lab_request.result
	except LabTestResult.DoesNotExist:
		return JsonResponse({'success': False, 'message': 'No result exists for this request.'}, status=404)

	# Permission check
	if not can_edit_result(request.user, result):
		return JsonResponse({'success': False, 'message': 'You do not have permission to edit this result.'}, status=403)

	if request.method == 'GET':
		# Return current result data as JSON for populating the edit modal
		param_results = []
		for pr in result.parameter_results.select_related('parameter').all():
			param_results.append({
				'parameter_id': pr.parameter_id,
				'result_value': pr.result_value,
				'notes': pr.notes,
			})
		return JsonResponse({
			'success': True,
			'result': {
				'overall_value': result.result_value,
				'interpretation': result.interpretation,
				'remarks': result.remarks,
				'is_abnormal': result.is_abnormal,
				'parameter_results': param_results,
			}
		})

	if request.method != 'POST':
		return JsonResponse({'success': False, 'message': 'GET or POST required.'}, status=405)

	# Update summary fields
	overall_value  = request.POST.get('overall_value', '').strip()
	interpretation = request.POST.get('interpretation', '').strip()
	remarks        = request.POST.get('remarks', '').strip()
	is_abnormal    = request.POST.get('is_abnormal') == '1'

	result.result_value = overall_value or result.result_value
	result.interpretation = interpretation
	result.remarks = remarks
	result.is_abnormal = is_abnormal
	result.save()

	# Update per-parameter values
	profile = lab_request.test.profile
	any_abnormal = False
	seen_param_ids = set()

	if profile:
		pps = TestProfileParameter.objects.filter(
			profile=profile
		).select_related('parameter').order_by('display_order', 'parameter__name')

		for pp in pps:
			seen_param_ids.add(pp.parameter_id)
			val = request.POST.get(f'param_{pp.parameter_id}', '').strip()
			notes = request.POST.get(f'param_{pp.parameter_id}_notes', '').strip()
			if not val:
				continue
			pr, created = ParameterResult.objects.get_or_create(
				test_result=result,
				parameter=pp.parameter,
				defaults={'result_value': val, 'notes': notes}
			)
			if not created:
				pr.result_value = val
				pr.notes = notes
				pr.save()
			if pr.flag in ('low', 'high', 'critical_low', 'critical_high', 'abnormal'):
				any_abnormal = True

	# Also update any existing ParameterResults not in the current profile
	for pr in result.parameter_results.select_related('parameter').all():
		if pr.parameter_id in seen_param_ids:
			continue
		val = request.POST.get(f'param_{pr.parameter_id}', '').strip()
		notes = request.POST.get(f'param_{pr.parameter_id}_notes', '').strip()
		if val:
			pr.result_value = val
			pr.notes = notes
			pr.save()
		if pr.flag in ('low', 'high', 'critical_low', 'critical_high', 'abnormal'):
			any_abnormal = True

	if any_abnormal and not is_abnormal:
		result.is_abnormal = True
		result.save(update_fields=['is_abnormal'])

	return JsonResponse({
		'success': True,
		'message': f'Results updated for {lab_request.test.name}.',
	})


@login_required
@lab_verify_required
def verify_result(request, pk):
	"""Verify a lab test result (lab_manager / pathologist only)"""
	result = get_object_or_404(LabTestResult, pk=pk)

	if result.verified:
		if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
			return JsonResponse({'success': False, 'message': 'Result is already verified.'}, status=400)
		messages.warning(request, 'Result is already verified.')
		return redirect('laboratory:request_detail', pk=result.request_id)

	result.verified = True
	result.verified_by = request.user
	result.verified_at = timezone.now()
	result.save(update_fields=['verified', 'verified_by', 'verified_at'])

	if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
		return JsonResponse({'success': True, 'message': 'Result verified successfully.'})
	messages.success(request, 'Result verified successfully.')
	return redirect('laboratory:request_detail', pk=result.request_id)


@login_required
@lab_verify_required
def unverify_result(request, pk):
	"""Unverify a lab test result (lab_manager / pathologist only)"""
	result = get_object_or_404(LabTestResult, pk=pk)

	if not result.verified:
		if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
			return JsonResponse({'success': False, 'message': 'Result is not verified.'}, status=400)
		messages.warning(request, 'Result is not verified.')
		return redirect('laboratory:request_detail', pk=result.request_id)

	result.verified = False
	result.verified_by = None
	result.verified_at = None
	result.save(update_fields=['verified', 'verified_by', 'verified_at'])

	if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
		return JsonResponse({'success': True, 'message': 'Result verification removed.'})
	messages.success(request, 'Result verification removed.')
	return redirect('laboratory:request_detail', pk=result.request_id)


@login_required
@app_access_required('laboratory')
def result_detail(request, pk):
	"""View details of a specific lab test result"""
	result = get_object_or_404(
		LabTestResult.objects.select_related(
			'request', 'request__patient', 'request__test', 
			'reported_by', 'verified_by'
		),
		pk=pk
	)
	
	# If AJAX request, return partial HTML for modal
	if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
		return render(request, 'laboratory/result_detail_partial.html', {'result': result})
	
	# Otherwise render full page
	context = {'result': result}
	return render(request, 'laboratory/result_detail.html', context)

# Test Parameter Views
@login_required
@lab_manage_required
def test_parameter_list(request):
	"""List all test parameters"""
	parameters = TestParameter.objects.all().order_by('display_order', 'name')
	context = {'parameters': parameters}
	return render(request, 'laboratory/test_parameter_list.html', context)

@login_required
@lab_manage_required
def test_parameter_add(request):
	"""Add a new test parameter"""
	if request.method == 'POST':
		form = TestParameterForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'Test parameter created successfully!')
			return redirect('laboratory:test_parameter_list')
	else:
		form = TestParameterForm()
	
	context = {'form': form, 'title': 'Add Test Parameter'}
	return render(request, 'laboratory/test_parameter_form.html', context)

@login_required
@lab_manage_required
def test_parameter_edit(request, pk):
	"""Edit a test parameter"""
	parameter = get_object_or_404(TestParameter, pk=pk)
	
	if request.method == 'POST':
		form = TestParameterForm(request.POST, instance=parameter)
		if form.is_valid():
			form.save()
			messages.success(request, 'Test parameter updated successfully!')
			return redirect('laboratory:test_parameter_list')
	else:
		form = TestParameterForm(instance=parameter)
	
	context = {'form': form, 'title': 'Edit Test Parameter', 'parameter': parameter}
	return render(request, 'laboratory/test_parameter_form.html', context)

# Test Profile Views
@login_required
@lab_manage_required
def test_profile_list(request):
	"""List all test profiles"""
	profiles = TestProfile.objects.all().order_by('name')
	context = {'profiles': profiles}
	return render(request, 'laboratory/test_profile_list.html', context)

@login_required
@lab_manage_required
def test_profile_add(request):
	"""Add a new test profile"""
	if request.method == 'POST':
		form = TestProfileForm(request.POST)
		if form.is_valid():
			profile = form.save()
			messages.success(request, 'Test profile created successfully!')
			return redirect('laboratory:test_profile_detail', pk=profile.pk)
	else:
		form = TestProfileForm()
	
	context = {'form': form, 'title': 'Add Test Profile'}
	return render(request, 'laboratory/test_profile_form.html', context)

@login_required
@lab_manage_required
def test_profile_edit(request, pk):
	"""Edit a test profile"""
	profile = get_object_or_404(TestProfile, pk=pk)
	
	if request.method == 'POST':
		form = TestProfileForm(request.POST, instance=profile)
		if form.is_valid():
			form.save()
			messages.success(request, 'Test profile updated successfully!')
			return redirect('laboratory:test_profile_detail', pk=profile.pk)
	else:
		form = TestProfileForm(instance=profile)
	
	context = {'form': form, 'title': 'Edit Test Profile', 'profile': profile}
	return render(request, 'laboratory/test_profile_form.html', context)

@login_required
@app_access_required('laboratory')
def test_profile_detail(request, pk):
	"""View test profile details"""
	profile = get_object_or_404(TestProfile.objects.prefetch_related('parameters'), pk=pk)
	parameters = profile.get_parameters_ordered()
	
	# Get available parameters to add
	available_parameters = TestParameter.objects.filter(is_active=True).exclude(
		id__in=profile.parameters.values_list('id', flat=True)
	).order_by('display_order', 'name')
	
	context = {
		'profile': profile,
		'parameters': parameters,
		'available_parameters': available_parameters,
	}
	return render(request, 'laboratory/test_profile_detail.html', context)

@login_required
@lab_manage_required
def test_profile_add_parameter(request, pk):
	"""Add parameter to test profile"""
	profile = get_object_or_404(TestProfile, pk=pk)
	parameter_id = request.POST.get('parameter')
	
	if parameter_id:
		parameter = get_object_or_404(TestParameter, pk=parameter_id)
		# Get the highest display_order for this profile
		max_order = TestProfileParameter.objects.filter(profile=profile).aggregate(
			Max('display_order'))['display_order__max'] or 0
		
		# Add parameter to profile
		TestProfileParameter.objects.create(
			profile=profile,
			parameter=parameter,
			display_order=max_order + 1
		)
		messages.success(request, f'{parameter.name} added to {profile.name}')
	
	return redirect('laboratory:test_profile_detail', pk=pk)

@login_required
@lab_manage_required
def test_profile_remove_parameter(request, pk, parameter_pk):
	"""Remove parameter from test profile"""
	profile = get_object_or_404(TestProfile, pk=pk)
	parameter = get_object_or_404(TestParameter, pk=parameter_pk)
	
	TestProfileParameter.objects.filter(profile=profile, parameter=parameter).delete()
	messages.success(request, f'{parameter.name} removed from {profile.name}')
	
	return redirect('laboratory:test_profile_detail', pk=pk)

@login_required
@lab_manage_required
def test_profile_reorder_parameters(request, pk):
	"""Reorder parameters in test profile"""
	profile = get_object_or_404(TestProfile, pk=pk)
	
	if request.method == 'POST':
		parameter_orders = request.POST.getlist('parameter_order')
		for index, param_pk in enumerate(parameter_orders):
			TestProfileParameter.objects.filter(
				profile=profile, 
				parameter_id=param_pk
			).update(display_order=index + 1)
		
		messages.success(request, 'Parameters reordered successfully!')
	
	return redirect('laboratory:test_profile_detail', pk=pk)

@login_required
@app_access_required('laboratory')
def test_certificate(request, pk):
	"""Printable lab test certificate/report — supports multiple lab request IDs via ?ids=1,2,3"""
	from clinic_settings.models import ClinicSettings
	import qrcode
	from io import BytesIO
	import base64
	
	# Check for multi-select IDs in query string
	ids_param = request.GET.get('ids', '')
	if ids_param:
		try:
			pk_list = [int(x) for x in ids_param.split(',') if x.strip()]
		except ValueError:
			pk_list = [pk]
	else:
		pk_list = [pk]
	
	lab_requests = list(
		LabTestRequest.objects.filter(pk__in=pk_list).select_related('patient', 'test', 'requested_by')
	)
	if not lab_requests:
		from django.http import Http404
		raise Http404("No lab requests found.")
	
	# Parse parameter selections for each test
	test_params_map = {}
	for lr in lab_requests:
		param_key = f'test_{lr.pk}_params'
		param_val = request.GET.get(param_key, '')
		if param_val:
			test_params_map[lr.pk] = [int(p) for p in param_val.split(',') if p.strip().isdigit()]
	
	# Build a list of {request, result, test, allowed_params} dicts for the template
	# Only include tests that have been completed (have a result)
	lab_request_data = []
	for lr in lab_requests:
		try:
			result = lr.result
		except LabTestResult.DoesNotExist:
			result = None
		if result is None:
			continue
		lab_request_data.append({
			'request_obj': lr,
			'test': lr.test,
			'result': result,
			'allowed_params': test_params_map.get(lr.pk, []),
		})
	
	# Use the first request for patient / primary info
	primary_request = lab_requests[0]
	patient = primary_request.patient
	
	# Get clinic settings for logo
	try:
		clinic_settings = ClinicSettings.objects.first()
	except:
		clinic_settings = None
	
	# Get latest vital signs for physical examination data
	latest_vitals = patient.vital_signs.first()
	
	# Get latest lab test for laboratory investigation data
	from patients.models import LabTest
	latest_lab_test = patient.lab_tests.first()
	
	# Parse selected sections — None means param absent (default all); '' means explicitly empty (show none)
	sections_param = request.GET.get('sections', None)
	if sections_param is None:
		selected_sections = ['patient', 'physical', 'labinv', 'results']
	else:
		selected_sections = [s.strip() for s in sections_param.split(',') if s.strip()]
	
	# Parse sub-item fields for each section
	def parse_fields(param_name, defaults):
		val = request.GET.get(param_name, '')
		if val:
			return [s.strip() for s in val.split(',') if s.strip()]
		return defaults
	
	patient_fields = parse_fields('patient_fields', [
		'patient_name', 'patient_id', 'age', 'gender', 'dob', 'blood_type', 'phone', 'email',
		'address', 'city', 'state', 'postal_code', 'country', 'nationality',
		'id_type', 'id_number', 'emergency_contact', 'emergency_phone', 'emergency_relation',
		'allergies', 'medical_history', 'current_medications',
		'insurance_provider', 'insurance_policy', 'insurance_group',
		'reason_for_visit', 'patient_group', 'test_date', 'registration_date'
	])
	physical_fields = parse_fields('physical_fields', ['eyes_ears', 'cardiovascular', 'respiratory', 'body_systems', 'skin_other', 'vital_signs'])
	labinv_fields = parse_fields('labinv_fields', ['urine', 'stool', 'blood', 'chemistry', 'elisa', 'other_tests'])
	
	# Build R2 public URL for QR code (same pattern as publish view)
	import re
	from django.conf import settings as _settings
	patient_name_raw = getattr(patient, 'get_full_name', lambda: str(patient))()
	if not patient_name_raw:
		patient_name_raw = str(patient)
	safe_name = re.sub(r'[^\w]', '_', patient_name_raw).strip('_') or f'Patient_{pk}'
	r2_public = getattr(_settings, 'R2_PUBLIC_URL', '').rstrip('/')
	r2_qr_url = f'{r2_public}/certificates/{safe_name}_certificate_{pk}.pdf' if r2_public else ''

	qr_url = (r2_qr_url or (primary_request.certificate_gdrive_url if primary_request.certificate_gdrive_url else '')
	          or (primary_request.certificate_pdf_url if primary_request.certificate_pdf_url else '')
	          or request.build_absolute_uri(request.path))
	qr = qrcode.QRCode(version=1, box_size=10, border=2)
	qr.add_data(qr_url)
	qr.make(fit=True)
	qr_img = qr.make_image(fill_color="black", back_color="white")
	
	# Convert QR code to base64 for embedding in HTML
	buffer = BytesIO()
	qr_img.save(buffer, format='PNG')
	qr_base64 = base64.b64encode(buffer.getvalue()).decode()

	comment = request.GET.get('comment', '')

	context = {
		'request_obj': primary_request,
		'patient': patient,
		'test': primary_request.test,
		'result': lab_request_data[0]['result'],
		'clinic_settings': clinic_settings,
		'vitals': latest_vitals,
		'lab_test': latest_lab_test,
		'lab_request_data': lab_request_data,
		'multi_test': len(lab_request_data) > 1,
		'qr_code': qr_base64,
		'cloud_url': primary_request.certificate_pdf_url,
		'gdrive_url': primary_request.certificate_gdrive_url,
		'comment': comment,
		'show_patient': 'patient' in selected_sections,
		'show_physical': 'physical' in selected_sections,
		'show_labinv': 'labinv' in selected_sections,
		'show_results': 'results' in selected_sections,
		# Patient info sub-fields - Basic
		'show_patient_name': 'patient_name' in patient_fields,
		'show_patient_id': 'patient_id' in patient_fields,
		'show_age': 'age' in patient_fields,
		'show_gender': 'gender' in patient_fields,
		'show_dob': 'dob' in patient_fields,
		'show_blood_type': 'blood_type' in patient_fields,
		# Contact
		'show_phone': 'phone' in patient_fields,
		'show_email': 'email' in patient_fields,
		# Address
		'show_address': 'address' in patient_fields,
		'show_city': 'city' in patient_fields,
		'show_state': 'state' in patient_fields,
		'show_postal_code': 'postal_code' in patient_fields,
		'show_country': 'country' in patient_fields,
		'show_nationality': 'nationality' in patient_fields,
		# Identification
		'show_id_type': 'id_type' in patient_fields,
		'show_id_number': 'id_number' in patient_fields,
		# Emergency Contact
		'show_emergency_contact': 'emergency_contact' in patient_fields,
		'show_emergency_phone': 'emergency_phone' in patient_fields,
		'show_emergency_relation': 'emergency_relation' in patient_fields,
		# Medical Info
		'show_allergies': 'allergies' in patient_fields,
		'show_medical_history': 'medical_history' in patient_fields,
		'show_current_medications': 'current_medications' in patient_fields,
		# Insurance
		'show_insurance_provider': 'insurance_provider' in patient_fields,
		'show_insurance_policy': 'insurance_policy' in patient_fields,
		'show_insurance_group': 'insurance_group' in patient_fields,
		# Visit Info
		'show_reason_for_visit': 'reason_for_visit' in patient_fields,
		'show_patient_group': 'patient_group' in patient_fields,
		'show_test_date': 'test_date' in patient_fields,
		'show_registration_date': 'registration_date' in patient_fields,
		# Physical exam sub-fields
		'show_eyes_ears': 'eyes_ears' in physical_fields,
		'show_cardiovascular': 'cardiovascular' in physical_fields,
		'show_respiratory': 'respiratory' in physical_fields,
		'show_body_systems': 'body_systems' in physical_fields,
		'show_skin_other': 'skin_other' in physical_fields,
		'show_vital_signs': 'vital_signs' in physical_fields,
		# Lab investigation sub-fields
		'show_urine': 'urine' in labinv_fields,
		'show_stool': 'stool' in labinv_fields,
		'show_blood': 'blood' in labinv_fields,
		'show_chemistry': 'chemistry' in labinv_fields,
		'show_elisa': 'elisa' in labinv_fields,
		'show_other_tests': 'other_tests' in labinv_fields,
	}
	return render(request, 'laboratory/test_certificate.html', context)


@login_required
@app_access_required('laboratory')
def test_certificate_patient(request, patient_id):
	"""Certificate generation for patient without lab test selection"""
	from clinic_settings.models import ClinicSettings
	from patients.models import Patient
	import qrcode
	from io import BytesIO
	import base64
	
	patient = get_object_or_404(Patient, patient_id=patient_id)
	
	# Check for multi-select IDs in query string (may be empty)
	ids_param = request.GET.get('ids', '')
	lab_request_data = []
	primary_request = None
	
	if ids_param:
		try:
			pk_list = [int(x) for x in ids_param.split(',') if x.strip()]
			lab_requests = list(
				LabTestRequest.objects.filter(pk__in=pk_list).select_related('patient', 'test', 'requested_by')
			)
			
			# Parse parameter selections for each test
			test_params_map = {}
			for lr in lab_requests:
				param_key = f'test_{lr.pk}_params'
				param_val = request.GET.get(param_key, '')
				if param_val:
					test_params_map[lr.pk] = [int(p) for p in param_val.split(',') if p.strip().isdigit()]
			
			for lr in lab_requests:
				try:
					result = lr.result
				except LabTestResult.DoesNotExist:
					result = None
				if result is None:
					continue
				lab_request_data.append({
					'request_obj': lr,
					'test': lr.test,
					'result': result,
					'allowed_params': test_params_map.get(lr.pk, []),
				})
			if lab_requests:
				primary_request = lab_requests[0]
		except ValueError:
			pass
	
	# Get clinic settings for logo
	try:
		clinic_settings = ClinicSettings.objects.first()
	except:
		clinic_settings = None
	
	# Get latest vital signs for physical examination data
	latest_vitals = patient.vital_signs.first()
	
	# Get latest lab test for laboratory investigation data
	from patients.models import LabTest
	latest_lab_test = patient.lab_tests.first()
	
	# Parse selected sections — None means param absent (default all); '' means explicitly empty (show none)
	sections_param = request.GET.get('sections', None)
	if sections_param is None:
		selected_sections = ['patient', 'physical', 'labinv', 'results']
	else:
		selected_sections = [s.strip() for s in sections_param.split(',') if s.strip()]
	
	# Parse sub-item fields for each section
	def parse_fields(param_name, defaults):
		val = request.GET.get(param_name, '')
		if val:
			return [s.strip() for s in val.split(',') if s.strip()]
		return defaults
	
	patient_fields = parse_fields('patient_fields', [
		'patient_name', 'patient_id', 'age', 'gender', 'dob', 'blood_type', 'phone', 'email',
		'address', 'city', 'state', 'postal_code', 'country', 'nationality',
		'id_type', 'id_number', 'emergency_contact', 'emergency_phone', 'emergency_relation',
		'allergies', 'medical_history', 'current_medications',
		'insurance_provider', 'insurance_policy', 'insurance_group',
		'reason_for_visit', 'patient_group', 'test_date', 'registration_date'
	])
	physical_fields = parse_fields('physical_fields', ['eyes_ears', 'cardiovascular', 'respiratory', 'body_systems', 'skin_other', 'vital_signs'])
	labinv_fields = parse_fields('labinv_fields', ['urine', 'stool', 'blood', 'chemistry', 'elisa', 'other_tests'])
	
	# Build R2 public URL for QR code (same pattern as publish view)
	import re
	from django.conf import settings as _settings
	patient_name_raw = getattr(patient, 'get_full_name', lambda: str(patient))()
	if not patient_name_raw:
		patient_name_raw = str(patient)
	safe_name = re.sub(r'[^\w]', '_', patient_name_raw).strip('_') or f'Patient_{patient_id}'
	r2_public = getattr(_settings, 'R2_PUBLIC_URL', '').rstrip('/')
	r2_qr_url = f'{r2_public}/certificates/{safe_name}_certificate_{primary_request.pk}.pdf' if (r2_public and primary_request) else ''

	qr_url = (r2_qr_url
	          or (primary_request.certificate_gdrive_url if (primary_request and primary_request.certificate_gdrive_url) else '')
	          or (primary_request.certificate_pdf_url if (primary_request and primary_request.certificate_pdf_url) else '')
	          or request.build_absolute_uri(request.path))
	qr = qrcode.QRCode(version=1, box_size=10, border=2)
	qr.add_data(qr_url)
	qr.make(fit=True)
	qr_img = qr.make_image(fill_color="black", back_color="white")
	
	# Convert QR code to base64 for embedding in HTML
	buffer = BytesIO()
	qr_img.save(buffer, format='PNG')
	qr_base64 = base64.b64encode(buffer.getvalue()).decode()
	
	context = {
		'request_obj': primary_request,
		'patient': patient,
		'test': primary_request.test if primary_request else None,
		'result': lab_request_data[0]['result'] if lab_request_data else None,
		'clinic_settings': clinic_settings,
		'vitals': latest_vitals,
		'lab_test': latest_lab_test,
		'lab_request_data': lab_request_data,
		'multi_test': len(lab_request_data) > 1,
		'qr_code': qr_base64,
		'cloud_url': primary_request.certificate_pdf_url if primary_request else '',
		'show_patient': 'patient' in selected_sections,
		'show_physical': 'physical' in selected_sections,
		'show_labinv': 'labinv' in selected_sections,
		'show_results': 'results' in selected_sections,
		# Patient info sub-fields - Basic
		'show_patient_name': 'patient_name' in patient_fields,
		'show_patient_id': 'patient_id' in patient_fields,
		'show_age': 'age' in patient_fields,
		'show_gender': 'gender' in patient_fields,
		'show_dob': 'dob' in patient_fields,
		'show_blood_type': 'blood_type' in patient_fields,
		# Contact
		'show_phone': 'phone' in patient_fields,
		'show_email': 'email' in patient_fields,
		# Address
		'show_address': 'address' in patient_fields,
		'show_city': 'city' in patient_fields,
		'show_state': 'state' in patient_fields,
		'show_postal_code': 'postal_code' in patient_fields,
		'show_country': 'country' in patient_fields,
		'show_nationality': 'nationality' in patient_fields,
		# Identification
		'show_id_type': 'id_type' in patient_fields,
		'show_id_number': 'id_number' in patient_fields,
		# Emergency Contact
		'show_emergency_contact': 'emergency_contact' in patient_fields,
		'show_emergency_phone': 'emergency_phone' in patient_fields,
		'show_emergency_relation': 'emergency_relation' in patient_fields,
		# Medical Info
		'show_allergies': 'allergies' in patient_fields,
		'show_medical_history': 'medical_history' in patient_fields,
		'show_current_medications': 'current_medications' in patient_fields,
		# Insurance
		'show_insurance_provider': 'insurance_provider' in patient_fields,
		'show_insurance_policy': 'insurance_policy' in patient_fields,
		'show_insurance_group': 'insurance_group' in patient_fields,
		# Visit Info
		'show_reason_for_visit': 'reason_for_visit' in patient_fields,
		'show_patient_group': 'patient_group' in patient_fields,
		'show_test_date': 'test_date' in patient_fields,
		'show_registration_date': 'registration_date' in patient_fields,
		# Physical exam sub-fields
		'show_eyes_ears': 'eyes_ears' in physical_fields,
		'show_cardiovascular': 'cardiovascular' in physical_fields,
		'show_respiratory': 'respiratory' in physical_fields,
		'show_body_systems': 'body_systems' in physical_fields,
		'show_skin_other': 'skin_other' in physical_fields,
		'show_vital_signs': 'vital_signs' in physical_fields,
		# Lab investigation sub-fields
		'show_urine': 'urine' in labinv_fields,
		'show_stool': 'stool' in labinv_fields,
		'show_blood': 'blood' in labinv_fields,
		'show_chemistry': 'chemistry' in labinv_fields,
		'show_elisa': 'elisa' in labinv_fields,
		'show_other_tests': 'other_tests' in labinv_fields,
		'comment': request.GET.get('comment', ''),
	}
	return render(request, 'laboratory/test_certificate.html', context)


@login_required
@app_access_required('laboratory')
def patient_lab_tests_json(request, patient_id):
	"""Return list of lab test requests for a patient as JSON (for selection popup)"""
	from patients.models import Patient
	patient = get_object_or_404(Patient, patient_id=patient_id)
	lab_requests = LabTestRequest.objects.filter(patient=patient).select_related('test').order_by('-date_requested')
	
	data = []
	for lr in lab_requests:
		has_result = hasattr(lr, 'result')
		parameters = []
		
		# Get parameters from test profile (not just from results)
		if lr.test.profile:
			profile_params = TestProfileParameter.objects.filter(
				profile=lr.test.profile
			).select_related('parameter').order_by('display_order', 'parameter__name')
			for pp in profile_params:
				parameters.append({
					'id': pp.parameter.pk,
					'name': pp.parameter.name,
					'unit': pp.parameter.unit or '',
				})
		
		data.append({
			'id': lr.pk,
			'test_name': lr.test.name,
			'test_code': lr.test.code,
			'date_requested': lr.date_requested.strftime('%d/%m/%Y') if lr.date_requested else '',
			'status': lr.status,
			'has_result': has_result,
			'parameters': parameters,
		})
	
	return JsonResponse({'lab_requests': data})


@login_required
def physical_exam_form(request, patient_id):
	"""Printable physical examination assessment form for a patient"""
	from patients.models import Patient
	from clinic_settings.models import ClinicSettings
	
	patient = get_object_or_404(Patient, patient_id=patient_id)
	
	try:
		clinic_settings = ClinicSettings.objects.first()
	except:
		clinic_settings = None
	
	context = {
		'patient': patient,
		'clinic_settings': clinic_settings,
	}
	return render(request, 'laboratory/physical_exam_form.html', context)

@login_required
@app_access_required('laboratory')
def test_usage_report(request, pk):
	"""Generate and download test usage report as CSV"""
	from datetime import timedelta
	import csv
	from django.http import HttpResponse
	
	test = get_object_or_404(LabTest, pk=pk)
	
	# Calculate statistics
	now = timezone.now()
	today = now.date()
	week_start = today - timedelta(days=today.weekday())
	month_start = today.replace(day=1)
	
	# Get all requests for this test
	all_requests = test.requests.select_related('patient', 'requested_by').order_by('-date_requested')
	
	# Create CSV response
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = f'attachment; filename="test_usage_report_{test.code}_{today}.csv"'
	
	writer = csv.writer(response)
	
	# Write header
	writer.writerow(['Test Usage Report'])
	writer.writerow(['Test Name:', test.name])
	writer.writerow(['Test Code:', test.code])
	writer.writerow(['Category:', test.category.name if test.category else 'Other'])
	writer.writerow(['Report Date:', today.strftime('%B %d, %Y')])
	writer.writerow([])
	
	# Write statistics summary
	writer.writerow(['STATISTICS SUMMARY'])
	writer.writerow(['Period', 'Count'])
	writer.writerow(['Total Requests', all_requests.count()])
	writer.writerow(['This Month', all_requests.filter(date_requested__date__gte=month_start).count()])
	writer.writerow(['This Week', all_requests.filter(date_requested__date__gte=week_start).count()])
	writer.writerow(['Today', all_requests.filter(date_requested__date=today).count()])
	writer.writerow(['Completed', all_requests.filter(status='completed').count()])
	writer.writerow(['Pending', all_requests.filter(status__in=['requested', 'sample_collected', 'in_progress']).count()])
	writer.writerow([])
	
	# Write detailed request list
	writer.writerow(['DETAILED REQUEST LIST'])
	writer.writerow(['Date Requested', 'Patient Name', 'Patient ID', 'Status', 'Priority', 'Requested By', 'Sample ID'])
	
	for req in all_requests:
		writer.writerow([
			req.date_requested.strftime('%Y-%m-%d %H:%M'),
			req.patient.get_full_name(),
			req.patient.patient_id,
			req.get_status_display(),
			req.get_priority_display(),
			req.requested_by.get_full_name() if req.requested_by else 'N/A',
			req.sample_id or 'N/A'
		])
	
	return response


@login_required
@app_access_required('laboratory')
def publish_certificate(request, pk):
	"""Generate pixel-perfect certificate PDF via Playwright/Edge, upload to Cloudinary."""
	import re, io, os, tempfile, base64
	import qrcode as qrcode_lib
	import cloudinary, cloudinary.uploader
	from pathlib import Path
	from django.http import JsonResponse
	from django.template.loader import render_to_string
	from clinic_settings.models import ClinicSettings

	lab_request = get_object_or_404(LabTestRequest, pk=pk)
	patient = lab_request.patient

	try:
		clinic_settings = ClinicSettings.objects.first()
	except Exception:
		clinic_settings = None

	try:
		result = lab_request.result
	except Exception:
		result = None

	# Build safe patient name for filename
	patient_name_raw = getattr(patient, 'get_full_name', lambda: str(patient))()
	if not patient_name_raw:
		patient_name_raw = str(patient)
	safe_name = re.sub(r'[^\w]', '_', patient_name_raw).strip('_') or f'Patient_{pk}'

	# Predict Cloudinary URL for upload
	folder = 'certificates'
	public_id_base = f'{safe_name}_certificate_{pk}'
	cloud_name = cloudinary.config().cloud_name
	predicted_url = f'https://res.cloudinary.com/{cloud_name}/raw/upload/{folder}/{public_id_base}.pdf?dl=1'

	# Generate QR code pointing to Cloudflare R2 public download URL
	from django.conf import settings as _settings
	r2_public = getattr(_settings, 'R2_PUBLIC_URL', '').rstrip('/')
	qr_url = f'{r2_public}/{folder}/{public_id_base}.pdf' if r2_public else predicted_url
	qr = qrcode_lib.QRCode(version=1, box_size=10, border=2)
	qr.add_data(qr_url)
	qr.make(fit=True)
	qr_img = qr.make_image(fill_color='black', back_color='white')
	buf = io.BytesIO()
	qr_img.save(buf, format='PNG')
	qr_base64 = base64.b64encode(buf.getvalue()).decode()

	# Parse sections & fields — same logic as test_certificate view
	sections_param = request.GET.get('sections', None)
	if sections_param is None:
		selected_sections = ['patient', 'physical', 'labinv', 'results']
	else:
		selected_sections = [s.strip() for s in sections_param.split(',') if s.strip()]

	def _parse_fields(param_name, defaults):
		val = request.GET.get(param_name, '')
		if val:
			return [s.strip() for s in val.split(',') if s.strip()]
		return defaults

	patient_fields = _parse_fields('patient_fields', [
		'patient_name', 'patient_id', 'age', 'gender', 'dob', 'blood_type', 'phone', 'email',
		'address', 'city', 'state', 'postal_code', 'country', 'nationality',
		'id_type', 'id_number', 'emergency_contact', 'emergency_phone', 'emergency_relation',
		'allergies', 'medical_history', 'current_medications',
		'insurance_provider', 'insurance_policy', 'insurance_group',
		'reason_for_visit', 'patient_group', 'test_date', 'registration_date',
	])
	physical_fields = _parse_fields('physical_fields', ['eyes_ears', 'cardiovascular', 'respiratory', 'body_systems', 'skin_other', 'vital_signs'])
	labinv_fields = _parse_fields('labinv_fields', ['urine', 'stool', 'blood', 'chemistry', 'elisa', 'other_tests'])

	# Respect per-test parameter selection
	param_key = f'test_{pk}_params'
	param_val = request.GET.get(param_key, '')
	allowed_params = [int(p) for p in param_val.split(',') if p.strip().isdigit()] if param_val else []

	# Fetch vitals & lab test for physical/labinv sections
	from patients.models import LabTest as PatientLabTest
	latest_vitals = patient.vital_signs.first()
	latest_lab_test = patient.lab_tests.first()

	context = {
		'request_obj': lab_request,
		'patient': patient,
		'test': lab_request.test,
		'result': result,
		'clinic_settings': clinic_settings,
		'vitals': latest_vitals,
		'lab_test': latest_lab_test,
		'qr_code': qr_base64,
		'cloud_url': predicted_url,
		'lab_request_data': [{'test': lab_request.test, 'result': result,
							   'request_obj': lab_request, 'allowed_params': allowed_params}],
		'multi_test': False,
		'show_patient': 'patient' in selected_sections,
		'show_physical': 'physical' in selected_sections,
		'show_labinv': 'labinv' in selected_sections,
		'show_results': 'results' in selected_sections,
		'show_patient_name': 'patient_name' in patient_fields,
		'show_patient_id': 'patient_id' in patient_fields,
		'show_age': 'age' in patient_fields,
		'show_gender': 'gender' in patient_fields,
		'show_dob': 'dob' in patient_fields,
		'show_blood_type': 'blood_type' in patient_fields,
		'show_phone': 'phone' in patient_fields,
		'show_email': 'email' in patient_fields,
		'show_address': 'address' in patient_fields,
		'show_city': 'city' in patient_fields,
		'show_state': 'state' in patient_fields,
		'show_postal_code': 'postal_code' in patient_fields,
		'show_country': 'country' in patient_fields,
		'show_nationality': 'nationality' in patient_fields,
		'show_id_type': 'id_type' in patient_fields,
		'show_id_number': 'id_number' in patient_fields,
		'show_emergency_contact': 'emergency_contact' in patient_fields,
		'show_emergency_phone': 'emergency_phone' in patient_fields,
		'show_emergency_relation': 'emergency_relation' in patient_fields,
		'show_allergies': 'allergies' in patient_fields,
		'show_medical_history': 'medical_history' in patient_fields,
		'show_current_medications': 'current_medications' in patient_fields,
		'show_insurance_provider': 'insurance_provider' in patient_fields,
		'show_insurance_policy': 'insurance_policy' in patient_fields,
		'show_insurance_group': 'insurance_group' in patient_fields,
		'show_reason_for_visit': 'reason_for_visit' in patient_fields,
		'show_patient_group': 'patient_group' in patient_fields,
		'show_test_date': 'test_date' in patient_fields,
		'show_registration_date': 'registration_date' in patient_fields,
		'show_eyes_ears': 'eyes_ears' in physical_fields,
		'show_cardiovascular': 'cardiovascular' in physical_fields,
		'show_respiratory': 'respiratory' in physical_fields,
		'show_body_systems': 'body_systems' in physical_fields,
		'show_skin_other': 'skin_other' in physical_fields,
		'show_vital_signs': 'vital_signs' in physical_fields,
		'show_urine': 'urine' in labinv_fields,
		'show_stool': 'stool' in labinv_fields,
		'show_blood': 'blood' in labinv_fields,
		'show_chemistry': 'chemistry' in labinv_fields,
		'show_elisa': 'elisa' in labinv_fields,
		'show_other_tests': 'other_tests' in labinv_fields,
	}

	base_url = request.build_absolute_uri('/')
	html_string = render_to_string('laboratory/test_certificate.html', context, request=request)
	# Inject base tag so relative media URLs resolve via the Django server
	html_string = html_string.replace('<head>', f'<head><base href="{base_url}">', 1)

	tmp_html = None
	try:
		with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as f:
			f.write(html_string)
			tmp_html = f.name
		from playwright.sync_api import sync_playwright
		with sync_playwright() as p:
			browser = p.chromium.launch(channel='msedge')
			page = browser.new_page()
			page.goto(Path(tmp_html).as_uri())
			page.wait_for_load_state('networkidle')
			pdf_bytes = page.pdf(
				print_background=True,
				format='A4',
				margin={'top': '0mm', 'right': '0mm', 'bottom': '0mm', 'left': '0mm'},
			)
			browser.close()
	except Exception as e:
		return JsonResponse({'success': False, 'error': f'PDF generation failed: {e}'}, status=500)
	finally:
		if tmp_html and os.path.exists(tmp_html):
			os.unlink(tmp_html)

	target = request.GET.get('target', 'all')  # 'cloudinary', 'firebase', or 'all'

	cloud_url = lab_request.certificate_pdf_url or ''
	gdrive_url = lab_request.certificate_gdrive_url or ''

	# Upload to Cloudinary
	if target in ('cloudinary', 'all'):
		try:
			upload_result = cloudinary.uploader.upload(
				io.BytesIO(pdf_bytes),
				resource_type='raw',
				folder=folder,
				public_id=public_id_base,
				overwrite=True,
				format='pdf',
			)
			secure_url = upload_result.get('secure_url', '')
			cloud_url = (secure_url + '?dl=1') if secure_url else predicted_url
		except Exception as e:
			return JsonResponse({'success': False, 'error': f'Cloudinary upload failed: {e}'}, status=500)

	# Upload to Firebase
	if target in ('firebase', 'all'):
		try:
			from clinic_system.gdrive_utils import upload_pdf_to_drive
			gdrive_url = upload_pdf_to_drive(
				pdf_bytes, f'{public_id_base}.pdf', subfolder='certificates',
			)
		except Exception as e:
			if target == 'firebase':
				return JsonResponse({'success': False, 'error': f'Firebase upload failed: {e}'}, status=500)
			import logging
			logging.getLogger(__name__).warning(f'Firebase upload failed for certificate {pk}: {e}')

	lab_request.certificate_pdf_url = cloud_url
	lab_request.certificate_gdrive_url = gdrive_url
	lab_request.save(update_fields=['certificate_pdf_url', 'certificate_gdrive_url'])

	return JsonResponse({'success': True, 'url': cloud_url, 'gdrive_url': gdrive_url})


@login_required
@app_access_required('laboratory')
def publish_report(request, pk):
	"""Generate pixel-perfect report PDF via Playwright/Edge, upload to Cloudinary."""
	import re, io, os, tempfile, base64
	import qrcode as qrcode_lib
	import cloudinary, cloudinary.uploader
	from pathlib import Path
	from django.http import JsonResponse
	from django.template.loader import render_to_string
	from clinic_settings.models import ClinicSettings

	lab_request = get_object_or_404(LabTestRequest, pk=pk)
	patient = lab_request.patient

	try:
		clinic_settings = ClinicSettings.objects.first()
	except Exception:
		clinic_settings = None

	try:
		result = lab_request.result
	except Exception:
		result = None

	from django.db.models import Case, When, IntegerField
	profile_parameters = []
	if lab_request.test.profile:
		# Custom ordering: physical, chemical, microscopic
		category_order = Case(
			When(parameter__category__code='physical', then=1),
			When(parameter__category__code='chemical', then=2),
			When(parameter__category__code='microscopic', then=3),
			default=4,
			output_field=IntegerField()
		)
		pps = TestProfileParameter.objects.filter(
			profile=lab_request.test.profile
		).select_related('parameter').order_by(category_order, 'display_order', 'parameter__name')
		param_results_map = {}
		if result:
			for pr in result.parameter_results.select_related('parameter').all():
				param_results_map[pr.parameter_id] = pr
		for pp in pps:
			profile_parameters.append({'param': pp.parameter, 'pr': param_results_map.get(pp.parameter_id)})

	# Build category_sections for template compatibility
	param_cats = set(item['param'].category.id for item in profile_parameters if item['param'].category)
	has_multiple_param_cats = len(param_cats) >= 1
	cat = lab_request.test.category
	cat_display = lab_request.test.category.name if lab_request.test.category else 'Other'
	category_sections = [{
		'category': cat,
		'category_display': cat_display,
		'tests': [{
			'request_obj': lab_request,
			'test': lab_request.test,
			'result': result,
			'profile_parameters': profile_parameters,
			'group_id': 1,
			'has_multiple_param_cats': has_multiple_param_cats,
		}],
	}]

	# Build safe patient name for filename
	patient_name_raw = getattr(patient, 'get_full_name', lambda: str(patient))()
	if not patient_name_raw:
		patient_name_raw = str(patient)
	safe_name = re.sub(r'[^\w]', '_', patient_name_raw).strip('_') or f'Patient_{pk}'

	# Predict Cloudinary URL for upload
	folder = 'reports'
	public_id_base = f'{safe_name}_report_{pk}'
	cloud_name = cloudinary.config().cloud_name
	predicted_url = f'https://res.cloudinary.com/{cloud_name}/raw/upload/{folder}/{public_id_base}.pdf?dl=1'

	# Generate QR code pointing to Cloudflare R2 public download URL
	from django.conf import settings as _settings
	r2_public = getattr(_settings, 'R2_PUBLIC_URL', '').rstrip('/')
	qr_url = f'{r2_public}/{folder}/{public_id_base}.pdf' if r2_public else predicted_url
	qr = qrcode_lib.QRCode(version=1, box_size=10, border=2)
	qr.add_data(qr_url)
	qr.make(fit=True)
	qr_img = qr.make_image(fill_color='black', back_color='white')
	buf = io.BytesIO()
	qr_img.save(buf, format='PNG')
	qr_base64 = base64.b64encode(buf.getvalue()).decode()

	# Parse sections & patient_fields — same logic as test_report view
	sections_param = request.GET.get('sections', None)
	if sections_param is None:
		selected_sections = ['patient', 'results']
	else:
		selected_sections = [s.strip() for s in sections_param.split(',') if s.strip()]

	comment = request.GET.get('comment', '')

	patient_fields_param = request.GET.get('patient_fields', '')
	if patient_fields_param:
		patient_fields = [s.strip() for s in patient_fields_param.split(',') if s.strip()]
	else:
		patient_fields = [
			'patient_name', 'patient_id', 'age', 'gender', 'dob', 'phone',
			'nationality', 'id_type', 'id_number', 'test_date', 'referring_doctor',
			'reason_for_test', 'clinical_notes',
		]

	# Respect per-test parameter selection
	param_key = f'test_{pk}_params'
	param_val = request.GET.get(param_key, '')
	allowed_params = [int(p) for p in param_val.split(',') if p.strip().isdigit()] if param_val else []
	if allowed_params:
		profile_parameters = [pp for pp in profile_parameters if pp['param'].id in allowed_params]
		# Recalculate after filtering
		param_cats = set(item['param'].category.id for item in profile_parameters if item['param'].category)
		has_multiple_param_cats = len(param_cats) >= 1
		# Rebuild category_sections with filtered params
		category_sections = [{
			'category': cat,
			'category_display': cat_display,
			'tests': [{
				'request_obj': lab_request,
				'test': lab_request.test,
				'result': result,
				'profile_parameters': profile_parameters,
				'group_id': 1,
				'has_multiple_param_cats': has_multiple_param_cats,
			}],
		}]

	# Report type & referring doctor info
	report_type = request.GET.get('report_type', 'final')
	ref_doctor = request.GET.get('ref_doctor', '')
	ref_location = request.GET.get('ref_location', '')
	ref_contact = request.GET.get('ref_contact', '')
	sample_type = lab_request.test.sample_type or (lab_request.test.profile.sample_type if lab_request.test.profile else '') or ''

	context = {
		'request': lab_request,
		'result': result,
		'profile_parameters': profile_parameters,
		'category_sections': category_sections,
		'multi_category': False,
		'clinic_settings': clinic_settings,
		'qr_code': qr_base64,
		'cloud_url': predicted_url,
		'comment': comment,
		'report_type': report_type,
		'ref_doctor': ref_doctor,
		'ref_location': ref_location,
		'ref_contact': ref_contact,
		'sample_type': sample_type,
		'show_patient': 'patient' in selected_sections,
		'show_results': 'results' in selected_sections,
		'show_patient_name': 'patient_name' in patient_fields,
		'show_patient_id': 'patient_id' in patient_fields,
		'show_age': 'age' in patient_fields,
		'show_gender': 'gender' in patient_fields,
		'show_dob': 'dob' in patient_fields,
		'show_phone': 'phone' in patient_fields,
		'show_nationality': 'nationality' in patient_fields,
		'show_id_type': 'id_type' in patient_fields,
		'show_id_number': 'id_number' in patient_fields,
		'show_test_date': 'test_date' in patient_fields,
		'show_referring_doctor': 'referring_doctor' in patient_fields,
		'show_reason_for_test': 'reason_for_test' in patient_fields,
		'show_clinical_notes': 'clinical_notes' in patient_fields,
	}

	base_url = request.build_absolute_uri('/')
	html_string = render_to_string('laboratory/test_report.html', context, request=request)
	# Inject base tag so relative media URLs resolve via the Django server
	html_string = html_string.replace('<head>', f'<head><base href="{base_url}">', 1)

	tmp_html = None
	try:
		with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as f:
			f.write(html_string)
			tmp_html = f.name
		from playwright.sync_api import sync_playwright
		with sync_playwright() as p:
			browser = p.chromium.launch(channel='msedge')
			page = browser.new_page()
			page.goto(Path(tmp_html).as_uri())
			page.wait_for_load_state('networkidle')
			pdf_bytes = page.pdf(
				print_background=True,
				format='A4',
				margin={'top': '0mm', 'right': '0mm', 'bottom': '10mm', 'left': '0mm'},
				display_header_footer=True,
				header_template='<span></span>',
				footer_template='<div style="width:100%;text-align:center;font-size:8px;color:#888;font-family:Arial,sans-serif;">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>',
			)
			browser.close()
	except Exception as e:
		return JsonResponse({'success': False, 'error': f'PDF generation failed: {e}'}, status=500)
	finally:
		if tmp_html and os.path.exists(tmp_html):
			os.unlink(tmp_html)

	target = request.GET.get('target', 'all')  # 'cloudinary', 'firebase', or 'all'

	cloud_url = lab_request.report_pdf_url or ''
	gdrive_url = lab_request.report_gdrive_url or ''

	# Upload to Cloudinary
	if target in ('cloudinary', 'all'):
		try:
			upload_result = cloudinary.uploader.upload(
				io.BytesIO(pdf_bytes),
				resource_type='raw',
				folder=folder,
				public_id=public_id_base,
				overwrite=True,
				format='pdf',
			)
			secure_url = upload_result.get('secure_url', '')
			cloud_url = (secure_url + '?dl=1') if secure_url else predicted_url
		except Exception as e:
			return JsonResponse({'success': False, 'error': f'Cloudinary upload failed: {e}'}, status=500)

	# Upload to Firebase
	if target in ('firebase', 'all'):
		try:
			from clinic_system.gdrive_utils import upload_pdf_to_drive
			gdrive_url = upload_pdf_to_drive(
				pdf_bytes, f'{public_id_base}.pdf', subfolder='reports',
			)
		except Exception as e:
			if target == 'firebase':
				return JsonResponse({'success': False, 'error': f'Firebase upload failed: {e}'}, status=500)
			import logging
			logging.getLogger(__name__).warning(f'Firebase upload failed for report {pk}: {e}')

	lab_request.report_pdf_url = cloud_url
	lab_request.report_gdrive_url = gdrive_url
	lab_request.save(update_fields=['report_pdf_url', 'report_gdrive_url'])

	return JsonResponse({'success': True, 'url': cloud_url, 'gdrive_url': gdrive_url})


@login_required
@app_access_required('laboratory')
def test_requests_results(request, pk):
	"""View all requests and results for a specific test with filters"""
	from django.db.models import Q
	from django.core.paginator import Paginator
	from datetime import datetime
	
	test = get_object_or_404(LabTest, pk=pk)
	
	# Get all requests for this test
	requests = LabTestRequest.objects.filter(test=test).select_related(
		'patient', 'result'
	).order_by('-date_requested')
	
	# Apply filters
	date_from = request.GET.get('date_from')
	date_to = request.GET.get('date_to')
	status = request.GET.get('status')
	patient_search = request.GET.get('patient')
	
	if date_from:
		try:
			date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
			requests = requests.filter(date_requested__date__gte=date_from_obj)
		except ValueError:
			date_from = None
	
	if date_to:
		try:
			date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
			requests = requests.filter(date_requested__date__lte=date_to_obj)
		except ValueError:
			date_to = None
	
	if status:
		requests = requests.filter(status=status)
	
	if patient_search:
		requests = requests.filter(
			Q(patient__first_name__icontains=patient_search) |
			Q(patient__last_name__icontains=patient_search) |
			Q(patient__patient_id__icontains=patient_search)
		)
	
	# Statistics
	total_requests = test.requests.count()
	completed_count = test.requests.filter(status='completed').count()
	
	# Pagination
	paginator = Paginator(requests, 25)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	
	context = {
		'test': test,
		'page_obj': page_obj,
		'total_requests': total_requests,
		'completed_count': completed_count,
		'date_from': date_from or '',
		'date_to': date_to or '',
		'status': status or '',
		'patient_search': patient_search or '',
	}
	return render(request, 'laboratory/test_requests_results.html', context)


@login_required
@app_access_required('laboratory')
def batch_export_reports(request):
	"""Batch export multiple lab test reports as PDFs in a ZIP file"""
	import zipfile
	import io
	from django.http import HttpResponse
	from django.template.loader import render_to_string
	from clinic_settings.models import ClinicSettings
	import qrcode
	import base64
	from collections import OrderedDict
	
	# Get list of test request IDs from POST data
	if request.method != 'POST':
		return JsonResponse({'success': False, 'error': 'POST request required'}, status=400)
	
	import json
	try:
		data = json.loads(request.body)
		test_ids = data.get('test_ids', [])
	except:
		return JsonResponse({'success': False, 'error': 'Invalid request data'}, status=400)
	
	if not test_ids:
		return JsonResponse({'success': False, 'error': 'No test IDs provided'}, status=400)
	
	# Fetch all requested lab tests
	lab_requests = LabTestRequest.objects.filter(
		pk__in=test_ids
	).select_related('patient', 'test', 'test__profile', 'requested_by').order_by('patient__last_name', 'pk')
	
	if not lab_requests.exists():
		return JsonResponse({'success': False, 'error': 'No valid test requests found'}, status=404)
	
	try:
		clinic_settings = ClinicSettings.objects.first()
	except:
		clinic_settings = None
	
	# Create ZIP file in memory
	zip_buffer = io.BytesIO()
	
	with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
		for lab_request in lab_requests:
			try:
				# Get result
				try:
					result = lab_request.result
				except LabTestResult.DoesNotExist:
					result = None
				
				# Build profile parameters
				from django.db.models import Case, When, IntegerField
				category_order_expr = Case(
					When(parameter__category__code='physical', then=1),
					When(parameter__category__code='chemical', then=2),
					When(parameter__category__code='microscopic', then=3),
					default=4,
					output_field=IntegerField()
				)
				
				profile_parameters = []
				if lab_request.test.profile:
					pps = TestProfileParameter.objects.filter(
						profile=lab_request.test.profile
					).select_related('parameter').order_by(category_order_expr, 'display_order', 'parameter__name')
					
					param_results_map = {}
					if result:
						for pr in result.parameter_results.select_related('parameter').all():
							param_results_map[pr.parameter_id] = pr
					
					for pp in pps:
						pr = param_results_map.get(pp.parameter_id)
						profile_parameters.append({'param': pp.parameter, 'pr': pr})
				
				# Build category sections
				param_cats = set(item['param'].category.id for item in profile_parameters if item['param'].category)
				has_multiple_param_cats = len(param_cats) >= 1
				cat = lab_request.test.category
				cat_display = lab_request.test.category.name if lab_request.test.category else 'Other'
				category_sections = [{
					'category': cat,
					'category_display': cat_display,
					'tests': [{
						'request_obj': lab_request,
						'test': lab_request.test,
						'result': result,
						'profile_parameters': profile_parameters,
						'group_id': 1,
						'has_multiple_param_cats': has_multiple_param_cats,
					}],
				}]
				
				# Generate QR code
				qr_url = request.build_absolute_uri(f'/laboratory/requests/{lab_request.pk}/report/')
				qr = qrcode.QRCode(version=1, box_size=10, border=2)
				qr.add_data(qr_url)
				qr.make(fit=True)
				qr_img = qr.make_image(fill_color="black", back_color="white")
				buffer = io.BytesIO()
				qr_img.save(buffer, format='PNG')
				qr_base64 = base64.b64encode(buffer.getvalue()).decode()
				
				# Sample type
				sample_type = lab_request.test.sample_type or (lab_request.test.profile.sample_type if lab_request.test.profile else '') or ''
				
				# Build context
				context = {
					'request': lab_request,
					'result': result,
					'profile_parameters': profile_parameters,
					'category_sections': category_sections,
					'multi_category': False,
					'clinic_settings': clinic_settings,
					'qr_code': qr_base64,
					'cloud_url': lab_request.report_pdf_url,
					'gdrive_url': lab_request.report_gdrive_url,
					'comment': '',
					'report_type': 'final',
					'ref_doctor': '',
					'ref_location': '',
					'ref_contact': '',
					'sample_type': sample_type,
					'show_patient': True,
					'show_results': True,
					'show_patient_name': True,
					'show_patient_id': True,
					'show_age': True,
					'show_gender': True,
					'show_dob': True,
					'show_phone': True,
					'show_nationality': True,
					'show_id_type': True,
					'show_id_number': True,
					'show_test_date': True,
					'show_referring_doctor': True,
					'show_reason_for_test': True,
					'show_clinical_notes': True,
				}
				
				# Render HTML
				html_content = render_to_string('laboratory/test_report.html', context, request=request)
				
				# Generate filename
				patient_name = lab_request.patient.get_full_name().replace(' ', '_')
				test_name = lab_request.test.name.replace(' ', '_')
				filename = f"{patient_name}_{test_name}_{lab_request.pk}.html"
				
				# Add to ZIP
				zip_file.writestr(filename, html_content)
				
			except Exception as e:
				# Log error but continue with other reports
				import logging
				logger = logging.getLogger(__name__)
				logger.error(f"Error generating report for test {lab_request.pk}: {str(e)}")
				continue
	
	# Prepare response
	zip_buffer.seek(0)
	response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
	response['Content-Disposition'] = f'attachment; filename="lab_reports_batch_{len(test_ids)}_tests.zip"'
	
	return response


@login_required
@app_access_required('laboratory')
def batch_export_reports_pdf(request):
	"""Batch export multiple lab test reports as actual PDFs in a ZIP file using Playwright"""
	import zipfile
	import io
	import os
	from django.http import HttpResponse, JsonResponse
	from django.template.loader import render_to_string
	from clinic_settings.models import ClinicSettings
	import qrcode
	import base64
	import logging
	
	logger = logging.getLogger(__name__)
	
	try:
		# Get list of test request IDs from POST data
		if request.method != 'POST':
			return JsonResponse({'success': False, 'error': 'POST request required'}, status=400)
		
		import json
		try:
			data = json.loads(request.body)
			test_ids = data.get('test_ids', [])
		except:
			return JsonResponse({'success': False, 'error': 'Invalid request data'}, status=400)
		
		if not test_ids:
			return JsonResponse({'success': False, 'error': 'No test IDs provided'}, status=400)
		
		# Fetch all requested lab tests
		lab_requests = LabTestRequest.objects.filter(
			pk__in=test_ids
		).select_related('patient', 'test', 'test__profile', 'requested_by').order_by('patient__last_name', 'pk')
		
		if not lab_requests.exists():
			return JsonResponse({'success': False, 'error': 'No valid test requests found'}, status=404)
		
		try:
			clinic_settings = ClinicSettings.objects.first()
		except:
			clinic_settings = None
		
		# Try to use Playwright for PDF generation
		try:
			from playwright.sync_api import sync_playwright
			use_playwright = True
		except ImportError:
			use_playwright = False
			logger.warning("Playwright not available, falling back to HTML export")
		
		# Create ZIP file in memory
		zip_buffer = io.BytesIO()
		
		# Helper function to run Playwright in a thread (to avoid async context issues)
		def generate_pdfs_with_playwright(lab_requests_list, clinic_settings_obj, base_url):
			"""Run Playwright in a synchronous context"""
			import os
			from playwright.sync_api import sync_playwright
			
			# Allow sync database operations in this thread
			os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
			
			pdfs = []
			with sync_playwright() as p:
				browser = p.chromium.launch()
				page = browser.new_page()
				
				for lab_request in lab_requests_list:
					try:
						# Generate HTML content
						html_content = generate_report_html_for_pdf(lab_request, clinic_settings_obj, base_url)
						
						# Generate filename
						patient_name = lab_request.patient.get_full_name().replace(' ', '_')
						test_name = lab_request.test.name.replace(' ', '_')
						filename = f"{patient_name}_{test_name}_{lab_request.pk}.pdf"
						
						# Convert HTML to PDF using Playwright
						page.set_content(html_content)
						pdf_bytes = page.pdf(format='A4', print_background=True)
						
						pdfs.append((filename, pdf_bytes))
						
					except Exception as e:
						logger.error(f"Error generating PDF for test {lab_request.pk}: {str(e)}", exc_info=True)
						continue
				
				browser.close()
			
			return pdfs
		
		with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
			if use_playwright:
				# Use Playwright to generate PDFs in a thread pool to avoid async context issues
				try:
					from concurrent.futures import ThreadPoolExecutor
					
					# Pre-load all database data to avoid async context issues in thread
					# Force evaluation of querysets and access all related objects
					lab_requests_data = []
					for lr in lab_requests:
						# Access all related objects to load them into memory
						_ = lr.patient.get_full_name()
						_ = lr.test.name
						_ = lr.test.category
						if lr.test.profile:
							_ = lr.test.profile.sample_type
						try:
							result = lr.result
							# Force load parameter results
							_ = list(result.parameter_results.select_related('parameter', 'parameter__category').all())
						except:
							pass
						
						lab_requests_data.append(lr)
					
					# Get base URL for QR codes (thread-safe)
					base_url = request.build_absolute_uri('/').rstrip('/')
					
					# Run Playwright in a separate thread
					with ThreadPoolExecutor(max_workers=1) as executor:
						future = executor.submit(generate_pdfs_with_playwright, lab_requests_data, clinic_settings, base_url)
						pdfs = future.result(timeout=300)  # 5 minute timeout
					
					logger.info(f"Generated {len(pdfs)} PDFs")
					
					# Add all PDFs to ZIP
					if not pdfs:
						logger.warning("No PDFs were generated")
						return JsonResponse({'success': False, 'error': 'No PDFs could be generated. Check server logs for details.'}, status=500)
					
					for filename, pdf_bytes in pdfs:
						logger.info(f"Adding {filename} to ZIP ({len(pdf_bytes)} bytes)")
						zip_file.writestr(filename, pdf_bytes)
						
				except Exception as e:
					logger.error(f"Playwright error: {str(e)}")
					return JsonResponse({'success': False, 'error': f'PDF generation failed: {str(e)}'}, status=500)
			else:
				# Fallback: Generate HTML files if Playwright not available
				for lab_request in lab_requests:
					try:
						html_content = generate_report_html(lab_request, request, clinic_settings)
						
						patient_name = lab_request.patient.get_full_name().replace(' ', '_')
						test_name = lab_request.test.name.replace(' ', '_')
						filename = f"{patient_name}_{test_name}_{lab_request.pk}.html"
						
						zip_file.writestr(filename, html_content)
						
					except Exception as e:
						logger.error(f"Error generating report for test {lab_request.pk}: {str(e)}")
						continue
		
		# Prepare response
		zip_buffer.seek(0)
		file_ext = 'pdf' if use_playwright else 'html'
		response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
		response['Content-Disposition'] = f'attachment; filename="lab_reports_batch_{len(test_ids)}_tests_{file_ext}.zip"'
		
		return response
		
	except Exception as e:
		logger.error(f"Unexpected error in batch_export_reports_pdf: {str(e)}", exc_info=True)
		return JsonResponse({'success': False, 'error': f'Export failed: {str(e)}'}, status=500)


def generate_report_html(lab_request, request, clinic_settings):
	"""Helper function to generate HTML content for a lab test report"""
	base_url = request.build_absolute_uri('/').rstrip('/')
	return generate_report_html_for_pdf(lab_request, clinic_settings, base_url)


def generate_report_html_for_pdf(lab_request, clinic_settings, base_url):
	"""Thread-safe helper function to generate HTML content for a lab test report"""
	from django.template.loader import render_to_string
	import qrcode
	import base64
	import io
	
	# Get result
	try:
		result = lab_request.result
	except LabTestResult.DoesNotExist:
		result = None
	
	# Build profile parameters
	from django.db.models import Case, When, IntegerField
	category_order_expr = Case(
		When(parameter__category__code='physical', then=1),
		When(parameter__category__code='chemical', then=2),
		When(parameter__category__code='microscopic', then=3),
		default=4,
		output_field=IntegerField()
	)
	
	profile_parameters = []
	if lab_request.test.profile:
		pps = TestProfileParameter.objects.filter(
			profile=lab_request.test.profile
		).select_related('parameter').order_by(category_order_expr, 'display_order', 'parameter__name')
		
		param_results_map = {}
		if result:
			for pr in result.parameter_results.select_related('parameter').all():
				param_results_map[pr.parameter_id] = pr
		
		for pp in pps:
			pr = param_results_map.get(pp.parameter_id)
			profile_parameters.append({'param': pp.parameter, 'pr': pr})
	
	# Build category sections
	param_cats = set(item['param'].category.id for item in profile_parameters if item['param'].category)
	has_multiple_param_cats = len(param_cats) >= 1
	cat = lab_request.test.category
	cat_display = lab_request.test.category.name if lab_request.test.category else 'Other'
	category_sections = [{
		'category': cat,
		'category_display': cat_display,
		'tests': [{
			'request_obj': lab_request,
			'test': lab_request.test,
			'result': result,
			'profile_parameters': profile_parameters,
			'group_id': 1,
			'has_multiple_param_cats': has_multiple_param_cats,
		}],
	}]
	
	# Generate QR code
	qr_url = f"{base_url}/laboratory/requests/{lab_request.pk}/report/"
	qr = qrcode.QRCode(version=1, box_size=10, border=2)
	qr.add_data(qr_url)
	qr.make(fit=True)
	qr_img = qr.make_image(fill_color="black", back_color="white")
	buffer = io.BytesIO()
	qr_img.save(buffer, format='PNG')
	qr_base64 = base64.b64encode(buffer.getvalue()).decode()
	
	# Sample type
	sample_type = lab_request.test.sample_type or (lab_request.test.profile.sample_type if lab_request.test.profile else '') or ''
	
	# Convert logo to base64 for embedding in PDF/HTML
	logo_base64 = None
	if clinic_settings and clinic_settings.logo:
		try:
			from django.core.files.storage import default_storage
			import mimetypes
			
			# Read logo file
			logo_file = clinic_settings.logo
			if hasattr(logo_file, 'read'):
				logo_data = logo_file.read()
				logo_file.seek(0)  # Reset file pointer
			else:
				# If it's a file path, read from storage
				with default_storage.open(logo_file.name, 'rb') as f:
					logo_data = f.read()
			
			# Determine MIME type
			mime_type = mimetypes.guess_type(logo_file.name)[0] or 'image/png'
			
			# Encode to base64
			logo_base64 = f"data:{mime_type};base64,{base64.b64encode(logo_data).decode()}"
		except Exception as e:
			import logging
			logger = logging.getLogger(__name__)
			logger.warning(f"Could not convert logo to base64: {str(e)}")
	
	# Build context
	context = {
		'request': lab_request,
		'result': result,
		'profile_parameters': profile_parameters,
		'category_sections': category_sections,
		'multi_category': False,
		'clinic_settings': clinic_settings,
		'logo_base64': logo_base64,
		'qr_code': qr_base64,
		'cloud_url': lab_request.report_pdf_url,
		'gdrive_url': lab_request.report_gdrive_url,
		'comment': '',
		'report_type': 'final',
		'ref_doctor': '',
		'ref_location': '',
		'ref_contact': '',
		'sample_type': sample_type,
		'show_patient': True,
		'show_results': True,
		'show_patient_name': True,
		'show_patient_id': True,
		'show_age': True,
		'show_gender': True,
		'show_dob': True,
		'show_phone': True,
		'show_nationality': True,
		'show_id_type': True,
		'show_id_number': True,
		'show_test_date': True,
		'show_referring_doctor': True,
		'show_reason_for_test': True,
		'show_clinical_notes': True,
	}
	
	# Render HTML without request object (thread-safe)
	return render_to_string('laboratory/test_report.html', context)


def generate_certificate_html_for_pdf(lab_request, clinic_settings, base_url):
	"""Thread-safe helper function to generate HTML content for a lab test certificate"""
	from django.template.loader import render_to_string
	import qrcode
	import base64
	import io
	
	# Get result
	try:
		result = lab_request.result
	except LabTestResult.DoesNotExist:
		result = None
	
	# Generate QR code
	qr_url = f"{base_url}/laboratory/requests/{lab_request.pk}/certificate/"
	qr = qrcode.QRCode(version=1, box_size=10, border=2)
	qr.add_data(qr_url)
	qr.make(fit=True)
	qr_img = qr.make_image(fill_color="black", back_color="white")
	buffer = io.BytesIO()
	qr_img.save(buffer, format='PNG')
	qr_base64 = base64.b64encode(buffer.getvalue()).decode()
	
	# Convert logo to base64 for embedding
	logo_base64 = None
	if clinic_settings and clinic_settings.logo:
		try:
			from django.core.files.storage import default_storage
			import mimetypes
			
			logo_file = clinic_settings.logo
			if hasattr(logo_file, 'read'):
				logo_data = logo_file.read()
				logo_file.seek(0)
			else:
				with default_storage.open(logo_file.name, 'rb') as f:
					logo_data = f.read()
			
			mime_type = mimetypes.guess_type(logo_file.name)[0] or 'image/png'
			logo_base64 = f"data:{mime_type};base64,{base64.b64encode(logo_data).decode()}"
		except Exception as e:
			import logging
			logger = logging.getLogger(__name__)
			logger.warning(f"Could not convert logo to base64: {str(e)}")
	
	# Build context for certificate template
	context = {
		'lab_request': lab_request,
		'patient': lab_request.patient,
		'test': lab_request.test,
		'result': result,
		'clinic_settings': clinic_settings,
		'logo_base64': logo_base64,
		'qr_code': qr_base64,
		'cloud_url': lab_request.certificate_pdf_url,
		'gdrive_url': lab_request.certificate_gdrive_url,
	}
	
	# Render certificate HTML template (same as test_certificate view uses)
	return render_to_string('laboratory/test_certificate.html', context)


@login_required
@app_access_required('laboratory')
def batch_upload_reports(request):
	"""Batch upload multiple lab test reports to Cloudflare R2"""
	import json
	import re
	from django.http import JsonResponse
	import logging
	
	logger = logging.getLogger(__name__)
	
	if request.method != 'POST':
		return JsonResponse({'success': False, 'error': 'POST request required'}, status=400)
	
	try:
		data = json.loads(request.body)
		test_ids = data.get('test_ids', [])
	except:
		return JsonResponse({'success': False, 'error': 'Invalid request data'}, status=400)
	
	if not test_ids:
		return JsonResponse({'success': False, 'error': 'No test IDs provided'}, status=400)
	
	# Fetch all requested lab tests
	lab_requests = LabTestRequest.objects.filter(
		pk__in=test_ids
	).select_related('patient', 'test', 'test__profile', 'requested_by')
	
	if not lab_requests.exists():
		return JsonResponse({'success': False, 'error': 'No valid test requests found'}, status=404)
	
	# Get clinic settings
	try:
		from clinic_settings.models import ClinicSettings
		clinic_settings = ClinicSettings.objects.first()
	except:
		clinic_settings = None
	
	# Check if Playwright is available
	try:
		from playwright.sync_api import sync_playwright
		use_playwright = True
	except ImportError:
		return JsonResponse({'success': False, 'error': 'Playwright not available. Cannot generate PDFs for upload.'}, status=500)
	
	uploaded_count = 0
	failed_uploads = []
	
	# Get base URL for QR codes
	base_url = request.build_absolute_uri('/').rstrip('/')
	
	# Process each report
	for lab_request in lab_requests:
		try:
			# Generate PDF using the same logic as batch_export_reports_pdf
			import os
			os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
			
			# Generate HTML content
			html_content = generate_report_html_for_pdf(lab_request, clinic_settings, base_url)
			
			# Generate PDF with Playwright
			with sync_playwright() as p:
				browser = p.chromium.launch()
				page = browser.new_page()
				page.set_content(html_content)
				pdf_bytes = page.pdf(format='A4', print_background=True)
				browser.close()
			
			# Build safe patient name for filename
			patient_name_raw = lab_request.patient.get_full_name()
			safe_name = re.sub(r'[^\w]', '_', patient_name_raw).strip('_') or f'Patient_{lab_request.pk}'
			
			# Upload to Cloudflare R2
			public_id_base = f'{safe_name}_report_{lab_request.pk}'
			
			try:
				from clinic_system.gdrive_utils import upload_pdf_to_drive
				r2_url = upload_pdf_to_drive(
					pdf_bytes, f'{public_id_base}.pdf', subfolder='reports',
				)
				
				# Update lab request with R2 URL
				lab_request.report_pdf_url = r2_url
				lab_request.report_gdrive_url = r2_url
				lab_request.save(update_fields=['report_pdf_url', 'report_gdrive_url'])
				
				uploaded_count += 1
				logger.info(f"Uploaded report {lab_request.pk} to Cloudflare R2: {r2_url}")
				
			except Exception as e:
				logger.error(f"Failed to upload report {lab_request.pk} to R2: {str(e)}")
				failed_uploads.append({
					'id': lab_request.pk,
					'patient': lab_request.patient.get_full_name(),
					'error': str(e)
				})
		
		except Exception as e:
			logger.error(f"Error processing report {lab_request.pk}: {str(e)}", exc_info=True)
			failed_uploads.append({
				'id': lab_request.pk,
				'patient': lab_request.patient.get_full_name() if hasattr(lab_request, 'patient') else 'Unknown',
				'error': str(e)
			})
	
	# Return results
	response_data = {
		'success': True,
		'uploaded_count': uploaded_count,
		'total_count': len(test_ids),
		'failed_count': len(failed_uploads),
	}
	
	if failed_uploads:
		response_data['failed_uploads'] = failed_uploads
	
	return JsonResponse(response_data)


@login_required
@app_access_required('laboratory')
def batch_download_tests(request):
	"""Batch download lab test reports or certificates based on selection"""
	import zipfile
	import io
	import json
	import logging
	
	logger = logging.getLogger(__name__)
	
	if request.method != 'POST':
		return JsonResponse({'success': False, 'error': 'POST request required'}, status=400)
	
	try:
		data = json.loads(request.body)
		test_ids = data.get('test_ids', [])
		download_format = data.get('format', 'reports')  # 'reports' or 'certificates' or 'both'
	except:
		return JsonResponse({'success': False, 'error': 'Invalid request data'}, status=400)
	
	if not test_ids:
		return JsonResponse({'success': False, 'error': 'No test IDs provided'}, status=400)
	
	# Fetch all requested lab tests
	lab_requests = LabTestRequest.objects.filter(
		pk__in=test_ids
	).select_related('patient', 'test', 'test__profile', 'test__category', 'requested_by').order_by('patient__last_name', 'pk')
	
	if not lab_requests.exists():
		return JsonResponse({'success': False, 'error': 'No valid test requests found'}, status=404)
	
	try:
		from clinic_settings.models import ClinicSettings
		clinic_settings = ClinicSettings.objects.first()
	except:
		clinic_settings = None
	
	# Check if Playwright is available
	try:
		from playwright.sync_api import sync_playwright
		use_playwright = True
	except ImportError:
		use_playwright = False
		logger.warning("Playwright not available, falling back to HTML export")
	
	# Get base URL for QR codes
	base_url = request.build_absolute_uri('/').rstrip('/')
	
	# Create ZIP file in memory
	zip_buffer = io.BytesIO()
	
	with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
		for lab_request in lab_requests:
			try:
				# Generate reports
				if download_format in ['reports', 'both']:
					try:
						if use_playwright:
							# Generate PDF with Playwright
							html_content = generate_report_html_for_pdf(lab_request, clinic_settings, base_url)
							
							with sync_playwright() as p:
								browser = p.chromium.launch()
								page = browser.new_page()
								page.set_content(html_content)
								pdf_bytes = page.pdf(format='A4', print_background=True)
								browser.close()
							
							filename = f"report_{lab_request.patient.last_name}_{lab_request.test.name}_{lab_request.pk}.pdf"
							zip_file.writestr(filename, pdf_bytes)
						else:
							# Fallback to HTML
							html_content = generate_report_html_for_pdf(lab_request, clinic_settings, base_url)
							filename = f"report_{lab_request.patient.last_name}_{lab_request.test.name}_{lab_request.pk}.html"
							zip_file.writestr(filename, html_content)
					
					except Exception as e:
						logger.error(f"Error generating report for test {lab_request.pk}: {str(e)}")
						continue
				
				# Generate certificates (only for completed tests)
				if download_format in ['certificates', 'both'] and lab_request.status == 'completed':
					try:
						if use_playwright:
							# Generate certificate HTML
							html_content = generate_certificate_html_for_pdf(lab_request, clinic_settings, base_url)
							
							with sync_playwright() as p:
								browser = p.chromium.launch()
								page = browser.new_page()
								page.set_content(html_content)
								pdf_bytes = page.pdf(format='A4', print_background=True)
								browser.close()
							
							filename = f"certificate_{lab_request.patient.last_name}_{lab_request.test.name}_{lab_request.pk}.pdf"
							zip_file.writestr(filename, pdf_bytes)
						else:
							# Fallback to HTML
							html_content = generate_certificate_html_for_pdf(lab_request, clinic_settings, base_url)
							filename = f"certificate_{lab_request.patient.last_name}_{lab_request.test.name}_{lab_request.pk}.html"
							zip_file.writestr(filename, html_content)
					
					except Exception as e:
						logger.error(f"Error generating certificate for test {lab_request.pk}: {str(e)}")
						continue
			
			except Exception as e:
				logger.error(f"Error processing test {lab_request.pk}: {str(e)}")
				continue
	
	# Prepare response
	zip_buffer.seek(0)
	file_ext = 'pdf' if use_playwright else 'html'
	response = HttpResponse(zip_buffer.read(), content_type='application/zip')
	response['Content-Disposition'] = f'attachment; filename="lab_tests_{download_format}_{file_ext}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.zip"'
	return response
