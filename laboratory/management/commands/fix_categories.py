"""
Management command to ensure all categories are registered and assigned.
- Creates any missing TestCategory and ParameterCategory entries.
- Assigns a default category to any LabTest or TestParameter that has NULL category.
"""
from django.core.management.base import BaseCommand
from laboratory.models import (
    TestCategory, ParameterCategory, LabTest, TestParameter, TestProfile
)


class Command(BaseCommand):
    help = 'Ensure all categories exist and are assigned to every test and parameter'

    # ── canonical test categories ──
    TEST_CATEGORIES = [
        ('hematology',    'Hematology',    1),
        ('biochemistry',  'Biochemistry',  2),
        ('microbiology',  'Microbiology',  3),
        ('serology',      'Serology',      4),
        ('immunology',    'Immunology',    5),
        ('pathology',     'Pathology',     6),
        ('urinalysis',    'Urinalysis',    7),
        ('parasitology',  'Parasitology',  8),
        ('coagulation',   'Coagulation',   9),
        ('other',         'Other',        99),
    ]

    # ── canonical parameter categories ──
    PARAM_CATEGORIES = [
        ('physical',    'Physical',    1),
        ('chemical',    'Chemical',    2),
        ('microscopic', 'Microscopic', 3),
        ('none',        'None',        99),
    ]

    def handle(self, *args, **options):
        # ── 1. Ensure TestCategory rows ──
        self.stdout.write(self.style.MIGRATE_HEADING('\n── Test Categories ──'))
        for code, name, order in self.TEST_CATEGORIES:
            obj, created = TestCategory.objects.get_or_create(
                code=code,
                defaults={'name': name, 'display_order': order, 'is_active': True},
            )
            tag = 'CREATED' if created else 'exists '
            self.stdout.write(f'  {tag}  {obj.name} (code={obj.code})')

        # ── 2. Ensure ParameterCategory rows ──
        self.stdout.write(self.style.MIGRATE_HEADING('\n── Parameter Categories ──'))
        for code, name, order in self.PARAM_CATEGORIES:
            obj, created = ParameterCategory.objects.get_or_create(
                code=code,
                defaults={'name': name, 'display_order': order, 'is_active': True},
            )
            tag = 'CREATED' if created else 'exists '
            self.stdout.write(f'  {tag}  {obj.name} (code={obj.code})')

        # ── 3. Assign missing TestCategory on LabTest ──
        default_test_cat = TestCategory.objects.get(code='other')
        orphan_tests = LabTest.objects.filter(category__isnull=True)
        count = orphan_tests.count()
        if count:
            orphan_tests.update(category=default_test_cat)
            self.stdout.write(self.style.WARNING(
                f'\n  Assigned "{default_test_cat.name}" to {count} LabTest(s) with no category.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('\n  All LabTests already have a category.'))

        # ── 4. Assign missing ParameterCategory on TestParameter ──
        default_param_cat = ParameterCategory.objects.get(code='none')
        orphan_params = TestParameter.objects.filter(category__isnull=True)
        count = orphan_params.count()
        if count:
            orphan_params.update(category=default_param_cat)
            self.stdout.write(self.style.WARNING(
                f'  Assigned "{default_param_cat.name}" to {count} TestParameter(s) with no category.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('  All TestParameters already have a category.'))

        # ── 5. Assign missing TestCategory on TestProfile ──
        orphan_profiles = TestProfile.objects.filter(category__isnull=True)
        count = orphan_profiles.count()
        if count:
            orphan_profiles.update(category=default_test_cat)
            self.stdout.write(self.style.WARNING(
                f'  Assigned "{default_test_cat.name}" to {count} TestProfile(s) with no category.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('  All TestProfiles already have a category.'))

        # ── 6. Summary report ──
        self.stdout.write(self.style.MIGRATE_HEADING('\n── Summary ──'))
        for cat in TestCategory.objects.all():
            t_count = LabTest.objects.filter(category=cat).count()
            p_count = TestProfile.objects.filter(category=cat).count()
            self.stdout.write(f'  {cat.name:20s}  tests={t_count}  profiles={p_count}')

        self.stdout.write('')
        for cat in ParameterCategory.objects.all():
            count = TestParameter.objects.filter(category=cat).count()
            self.stdout.write(f'  {cat.name:20s}  parameters={count}')

        self.stdout.write(self.style.SUCCESS('\nDone.'))
