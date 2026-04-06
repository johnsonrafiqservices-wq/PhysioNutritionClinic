"""
Management command: add CBC results for a named patient.

Usage:
    python manage.py add_cbc_result --patient kisa
    python manage.py add_cbc_result --patient kisa --request-id 42
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from laboratory.models import (
    LabTest, LabTestRequest, LabTestResult,
    TestParameter, TestProfileParameter, ParameterResult,
)
from patients.models import Patient


# ---------------------------------------------------------------------------
# Result values from the Sysmex analyser printout
# key = TestParameter code, value = result string
# ---------------------------------------------------------------------------
RESULT_VALUES = {
    'WBC':     '6.44',
    'NEU_ABS': '2.56',
    'LYM_ABS': '2.49',
    'MON_ABS': '0.43',
    'EOS_ABS': '0.95',
    'BAS_ABS': '0.01',
    'IMG_ABS': '0.03',
    'NEU_PCT': '39.8',
    'LYM_PCT': '38.6',
    'MON_PCT': '6.7',
    'EOS_PCT': '14.7',
    'BAS_PCT': '0.2',
    'IMG_PCT': '0.5',
    'RBC':     '5.81',
    'HGB':     '14.7',
    'HCT':     '44.5',
    'MCV':     '76.6',
    'MCH':     '25.4',
    'MCHC':    '33.0',
    'RDWCV':   '13.8',
    'RDWSD':   '39.2',
    'PLT':     '131',
    'MPV':     '11.5',
    'PDW':     '16.8',
    'PCT':     '0.151',
    'PLCC':    '49',
    'PLCR':    '37.4',
    'NRBC_A':  '0.000',
    'NRBC_P':  '0.00',
}


class Command(BaseCommand):
    help = 'Add CBC result values for a patient (by name search)'

    def add_arguments(self, parser):
        parser.add_argument('--patient', required=True, help='Patient name (partial match)')
        parser.add_argument('--request-id', type=int, default=None,
                            help='Specific LabTestRequest ID (optional)')

    @transaction.atomic
    def handle(self, *args, **options):
        name_query = options['patient']
        req_id = options.get('request_id')

        # --- 1. Find patient ---
        patients = Patient.objects.filter(
            first_name__icontains=name_query
        ) | Patient.objects.filter(
            last_name__icontains=name_query
        )
        patients = patients.distinct()

        if not patients.exists():
            self.stderr.write(self.style.ERROR(f'No patient found matching "{name_query}"'))
            return
        if patients.count() > 1:
            self.stdout.write(self.style.WARNING('Multiple patients found:'))
            for p in patients:
                self.stdout.write(f'  ID={p.pk}  {p.get_full_name()}  ({p.patient_id})')
            self.stderr.write(self.style.ERROR(
                'Narrow down: run again with a more specific name, or use --request-id'
            ))
            if not req_id:
                return
        patient = patients.first()
        self.stdout.write(f'Patient: {patient.get_full_name()} ({patient.patient_id})')

        # --- 2. Find CBC lab request ---
        cbc_test = LabTest.objects.filter(code='CBC').first()
        if not cbc_test:
            self.stderr.write(self.style.ERROR('No LabTest with code "CBC" found.'))
            return

        if req_id:
            qs = LabTestRequest.objects.filter(pk=req_id, test=cbc_test)
        else:
            qs = LabTestRequest.objects.filter(
                patient=patient, test=cbc_test
            ).exclude(status='cancelled').order_by('-date_requested')

        if not qs.exists():
            self.stderr.write(self.style.ERROR(
                f'No CBC request found for {patient.get_full_name()}.'
            ))
            return

        lab_request = qs.first()

        # Check if result already exists
        if hasattr(lab_request, 'result'):
            self.stdout.write(self.style.WARNING(
                f'Request REQ-{lab_request.pk:05d} already has a result. Updating existing result.'
            ))
            result = lab_request.result
        else:
            result = LabTestResult(
                request=lab_request,
                result_value='See parameters',
                is_abnormal=True,
            )
            result.save()
            self.stdout.write(f'  Created result for REQ-{lab_request.pk:05d}')

        # --- 3. Get profile parameters in order ---
        profile = cbc_test.profile
        if not profile:
            self.stderr.write(self.style.ERROR('CBC test has no profile. Run setup_cbc_parameters first.'))
            return

        pps = TestProfileParameter.objects.filter(
            profile=profile
        ).select_related('parameter').order_by('display_order')

        if not pps.exists():
            self.stderr.write(self.style.ERROR('CBC profile has no parameters.'))
            return

        # --- 4. Save ParameterResult for each parameter ---
        saved = 0
        skipped = 0
        any_abnormal = False
        for pp in pps:
            param = pp.parameter
            val = RESULT_VALUES.get(param.code)
            if val is None:
                self.stdout.write(
                    self.style.WARNING(f'  No result value for code "{param.code}" — skipping')
                )
                skipped += 1
                continue

            pr, created = ParameterResult.objects.update_or_create(
                test_result=result,
                parameter=param,
                defaults={'result_value': val, 'notes': ''},
            )
            pr.save()   # triggers flag evaluation
            if pr.flag in ('low', 'high', 'critical_low', 'critical_high', 'abnormal'):
                any_abnormal = True
            action = 'Created' if created else 'Updated'
            flag_str = f' [{pr.flag.upper()}]' if pr.flag and pr.flag != 'normal' else ''
            self.stdout.write(f'  {action}: {param.name} ({param.code}) = {val}{flag_str}')
            saved += 1

        # Update overall is_abnormal
        result.is_abnormal = any_abnormal
        result.save(update_fields=['is_abnormal'])

        # Update request status
        lab_request.status = 'completed'
        lab_request.save(update_fields=['status'])

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! {saved} parameter results saved, {skipped} skipped.\n'
            f'Request status set to: completed\n'
            f'Overall abnormal: {any_abnormal}'
        ))
