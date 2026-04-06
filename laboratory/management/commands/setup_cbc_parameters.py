"""
Management command: set up the 29-parameter CBC profile from the Sysmex analyser layout.

Usage:
    python manage.py setup_cbc_parameters
"""
from django.core.management.base import BaseCommand
from laboratory.models import (
    LabTest, TestProfile, TestParameter, TestProfileParameter, TestCategory,
)


# ---------------------------------------------------------------------------
# 29 parameters exactly as shown on the Sysmex CBC report layout
# ---------------------------------------------------------------------------
CBC_PARAMETERS = [
    # name               code       unit          ref_min   ref_max   ref_text         flag_criteria    critical_low  critical_high
    ('WBC',              'WBC',     '10\u2079/L',  4.00,    12.00,    None,            'range',         2.0,          30.0),
    ('Neu#',             'NEU_ABS', '10\u2079/L',  2.00,    8.00,     None,            'range',         0.5,          20.0),
    ('Lym#',             'LYM_ABS', '10\u2079/L',  0.80,    7.00,     None,            'range',         0.5,          None),
    ('Mon#',             'MON_ABS', '10\u2079/L',  0.12,    1.20,     None,            'range',         None,         None),
    ('Eos#',             'EOS_ABS', '10\u2079/L',  0.02,    0.80,     None,            'range',         None,         None),
    ('Bas#',             'BAS_ABS', '10\u2079/L',  0.00,    0.10,     None,            'range',         None,         None),
    ('IMG#',             'IMG_ABS', '10\u2079/L',  0.00,    0.10,     '0.00 - 999.99', 'range',         None,         None),
    ('Neu%',             'NEU_PCT', '%',           50.00,   70.00,    None,            'range',         None,         None),
    ('Lym%',             'LYM_PCT', '%',           20.00,   60.00,    None,            'range',         None,         None),
    ('Mon%',             'MON_PCT', '%',            3.00,   12.00,    None,            'range',         None,         None),
    ('Eos%',             'EOS_PCT', '%',            0.50,    5.00,    None,            'range',         None,         None),
    ('Bas%',             'BAS_PCT', '%',            0.00,    1.00,    None,            'range',         None,         None),
    ('IMG%',             'IMG_PCT', '%',            0.00,    1.00,    None,            'range',         None,         None),
    ('RBC',              'RBC',     '10\u00b9\u00b2/L', 3.50, 5.20,  None,            'range',         2.5,           7.0),
    ('HGB',              'HGB',     'g/dL',        12.00,   16.00,    None,            'range',         7.0,          20.0),
    ('HCT',              'HCT',     '%',           35.00,   49.00,    None,            'range',         21.0,         60.0),
    ('MCV',              'MCV',     'fL',          80.00,  100.00,    None,            'range',         None,         None),
    ('MCH',              'MCH',     'pg',          27.00,   34.00,    None,            'range',         None,         None),
    ('MCHC',             'MCHC',    'g/dL',        31.00,   37.00,    None,            'range',         None,         None),
    ('RDW-CV',           'RDWCV',   '%',           11.00,   16.00,    None,            'range',         None,         None),
    ('RDW-SD',           'RDWSD',   'fL',          35.00,   56.00,    None,            'range',         None,         None),
    ('PLT',              'PLT',     '10\u2079/L', 100.00,  300.00,    None,            'range',         50.0,       1000.0),
    ('MPV',              'MPV',     'fL',           6.50,   12.00,    None,            'range',         None,         None),
    ('PDW',              'PDW',     'fL',          15.00,   17.00,    None,            'range',         None,         None),
    ('PCT',              'PCT',     '%',            0.108,   0.282,   None,            'range',         None,         None),
    ('P-LCC',            'PLCC',    '10\u2079/L',  30.00,   90.00,   None,            'range',         None,         None),
    ('P-LCR',            'PLCR',    '%',           11.00,   45.00,    None,            'range',         None,         None),
    ('NRBC#',            'NRBC_A',  '10\u2079/L',  0.000,   0.100,   None,            'range',         None,         None),
    ('NRBC%',            'NRBC_P',  '/100WBC',     0.00,    0.30,    None,            'range',         None,         None),
]


class Command(BaseCommand):
    help = 'Replace CBC test parameters with the 29-parameter Sysmex analyser layout'

    def handle(self, *args, **options):
        # --- 1. Find the CBC LabTest ---
        try:
            lab_test = LabTest.objects.get(code='CBC')
        except LabTest.DoesNotExist:
            self.stderr.write(self.style.ERROR(
                'No LabTest with code "CBC" found. '
                'Create the CBC test first via the admin or lab-test UI.'
            ))
            return

        self.stdout.write(f'Found test: {lab_test}')

        # --- 2. Ensure a TestProfile is linked ---
        if not lab_test.profile_id:
            profile = TestProfile.objects.create(
                name=lab_test.name,
                code=lab_test.code,
                category=lab_test.category,
                sample_type=lab_test.sample_type or 'Blood (EDTA)',
                price=lab_test.price,
                currency=lab_test.currency,
                duration_hours=lab_test.duration_hours,
            )
            lab_test.profile = profile
            lab_test.save(update_fields=['profile'])
            self.stdout.write(self.style.SUCCESS(f'  Created new profile: {profile.code}'))
        else:
            profile = lab_test.profile
            self.stdout.write(f'  Using existing profile: {profile.code}')

        # --- 3. Clear old profile-parameter links (NOT the parameter records themselves) ---
        removed = TestProfileParameter.objects.filter(profile=profile).count()
        TestProfileParameter.objects.filter(profile=profile).delete()
        self.stdout.write(f'  Removed {removed} old parameter links')

        # --- 4. Create / update TestParameter records and link them ---
        created_count = updated_count = 0
        for order, row in enumerate(CBC_PARAMETERS, start=1):
            (
                name, code, unit,
                ref_min, ref_max, ref_text,
                flag_criteria,
                critical_low, critical_high,
            ) = row

            defaults = dict(
                name=name,
                unit=unit,
                result_type='numeric',
                reference_range_min=ref_min,
                reference_range_max=ref_max,
                reference_range_text=ref_text or '',
                flag_criteria=flag_criteria,
                critical_low=critical_low,
                critical_high=critical_high,
                category=None,
            )

            param, created = TestParameter.objects.update_or_create(
                code=code,
                defaults=defaults,
            )

            TestProfileParameter.objects.create(
                profile=profile,
                parameter=param,
                display_order=order,
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone! {created_count} parameters created, {updated_count} updated.\n'
                f'CBC now has {len(CBC_PARAMETERS)} parameters linked in order.'
            )
        )
