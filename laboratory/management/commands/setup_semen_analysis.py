"""
Management command: set up the Semen Analysis test profile with all parameters
from the standard report layout (Physical, Microscopic, Chemical examinations).

Usage:
    python manage.py setup_semen_analysis
"""
from django.core.management.base import BaseCommand
from laboratory.models import (
    LabTest, TestProfile, TestParameter, TestProfileParameter,
    ParameterCategory,
)


# ---------------------------------------------------------------------------
# Parameter categories (sections on the report)
# ---------------------------------------------------------------------------
CATEGORIES = [
    # (name, code, display_order)
    ('Physical Examination',    'SEMEN_PHYS', 1),
    ('Microscopic Examination', 'SEMEN_MICRO', 2),
    ('Chemical Examination',    'SEMEN_CHEM', 3),
]

# ---------------------------------------------------------------------------
# Parameters exactly as shown on the Semen Analysis report
# (category_code, name, code, result_type, unit, ref_min, ref_max, ref_text, flag_criteria)
# ---------------------------------------------------------------------------
SEMEN_PARAMETERS = [
    # ── Physical Examination ──
    ('SEMEN_PHYS', 'Appearance',                       'SEM_APPEAR',   'text',              '',      None,  None,  '',                       'none'),
    ('SEMEN_PHYS', 'PH',                               'SEM_PH',      'numeric',           '',      7.2,   8.0,   'Normal : 7.2 - 8.0',    'range'),
    ('SEMEN_PHYS', 'Volume',                            'SEM_VOL',     'numeric',           'ml',    2.0,   None,  '2.0 mL or more',        'range'),
    ('SEMEN_PHYS', 'Liquefaction Time',                 'SEM_LIQ',     'numeric',           'min',   None,  60.0,  'Completed within 60 min','range'),
    ('SEMEN_PHYS', 'Viscosity',                         'SEM_VISC',    'text',              '',      None,  None,  'Normal',                 'none'),
    ('SEMEN_PHYS', 'Sperm Agglutination-Antisperm Ab',  'SEM_AGGLUT',  'positive_negative', '',      None,  None,  '',                       'positive_negative'),

    # ── Microscopic Examination ──
    ('SEMEN_MICRO', 'Sperm Count (million/mL)',         'SEM_COUNT',   'numeric',           'million/mL', 20.0, None, '>=20',                'range'),
    ('SEMEN_MICRO', 'Sperm Viability',                  'SEM_VIAB',    'percentage',        '%',     None,  None,  '',                       'none'),
    ('SEMEN_MICRO', 'Sperm Morphology',                 'SEM_MORPH',   'normal_abnormal',   '',      None,  None,  '',                       'normal_abnormal'),
    ('SEMEN_MICRO', 'WBC',                              'SEM_WBC',     'numeric',           '',      None,  None,  '',                       'none'),
    ('SEMEN_MICRO', 'Gram Staining',                    'SEM_GRAM',    'normal_abnormal',   '',      None,  None,  '',                       'normal_abnormal'),

    # ── Chemical Examination ──
    ('SEMEN_CHEM', 'Fructose in semen',                 'SEM_FRUCT',   'text',              'mmol/l', None, None,  '10.0 - 30.0',           'none'),
    ('SEMEN_CHEM', 'Motility',                          'SEM_MOT',     'numeric',           '%',     None,  None,  '%',                      'none'),
    ('SEMEN_CHEM', 'a: Rapid Progressive',              'SEM_MOT_A',   'numeric',           '%',     None,  None,  '',                       'none'),
    ('SEMEN_CHEM', 'b: Moderate Progressive',           'SEM_MOT_B',   'numeric',           '%',     None,  None,  '',                       'none'),
    ('SEMEN_CHEM', 'c: Slow Progressive',               'SEM_MOT_C',   'numeric',           '%',     None,  None,  '',                       'none'),
]


class Command(BaseCommand):
    help = 'Set up or update the Semen Analysis test with all report parameters'

    def add_arguments(self, parser):
        parser.add_argument(
            '--code', default='SEMEN',
            help='LabTest code to look up (default: SEMEN)',
        )

    def handle(self, *args, **options):
        test_code = options['code']

        # --- 1. Find the Semen Analysis LabTest ---
        try:
            lab_test = LabTest.objects.get(code=test_code)
        except LabTest.DoesNotExist:
            # Try a broader search
            lab_test = LabTest.objects.filter(name__icontains='semen').first()
            if not lab_test:
                self.stderr.write(self.style.ERROR(
                    f'No LabTest with code "{test_code}" or name containing "semen" found.\n'
                    'Available lab tests:'
                ))
                for lt in LabTest.objects.filter(is_active=True).order_by('name')[:30]:
                    self.stderr.write(f'  [{lt.code}] {lt.name}')
                return

        self.stdout.write(f'Found test: {lab_test} (code={lab_test.code}, id={lab_test.id})')

        # --- 2. Create parameter categories ---
        cat_map = {}
        for cat_name, cat_code, cat_order in CATEGORIES:
            # Try by code first, then by name (both are unique)
            cat = ParameterCategory.objects.filter(code=cat_code).first()
            if not cat:
                cat = ParameterCategory.objects.filter(name=cat_name).first()
            if cat:
                cat.display_order = cat_order
                cat.save(update_fields=['display_order'])
                self.stdout.write(f'  Using existing category: {cat.name} ({cat.code})')
            else:
                cat = ParameterCategory.objects.create(
                    name=cat_name, code=cat_code, display_order=cat_order,
                )
                self.stdout.write(self.style.SUCCESS(f'  Created category: {cat_name}'))
            cat_map[cat_code] = cat

        # --- 3. Ensure a TestProfile is linked ---
        if not lab_test.profile_id:
            profile = TestProfile.objects.create(
                name=lab_test.name,
                code=lab_test.code + '_PROFILE',
                category=lab_test.category,
                sample_type=lab_test.sample_type or 'Semen',
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

        # --- 4. Clear old profile-parameter links ---
        removed = TestProfileParameter.objects.filter(profile=profile).count()
        TestProfileParameter.objects.filter(profile=profile).delete()
        self.stdout.write(f'  Removed {removed} old parameter links')

        # --- 5. Create / update TestParameter records and link them ---
        created_count = updated_count = 0
        for order, row in enumerate(SEMEN_PARAMETERS, start=1):
            (
                cat_code, name, code, result_type, unit,
                ref_min, ref_max, ref_text, flag_criteria,
            ) = row

            defaults = dict(
                name=name,
                unit=unit,
                result_type=result_type,
                reference_range_min=ref_min,
                reference_range_max=ref_max,
                reference_range_text=ref_text or '',
                flag_criteria=flag_criteria,
                category=cat_map.get(cat_code),
                display_order=order,
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
                f'Semen Analysis now has {len(SEMEN_PARAMETERS)} parameters linked in order.\n'
                f'Sections: Physical Examination (6), Microscopic Examination (5), Chemical Examination (5)'
            )
        )
