"""
Assign correct TestCategory to each LabTest based on test name/code,
and sync the linked TestProfile category.
"""
from django.core.management.base import BaseCommand
from laboratory.models import TestCategory, LabTest, TestProfile


# Map test codes → category codes
TEST_MAP = {
    # Hematology
    'CBC':           'hematology',
    'ESR':           'hematology',
    'BLOOD-GROUP':   'hematology',
    'PT-INR':        'coagulation',

    # Biochemistry
    'FBS':           'biochemistry',
    'RBS':           'biochemistry',
    'HBA1C':         'biochemistry',
    'LIPID':         'biochemistry',
    'KFT':           'biochemistry',
    'LFT':           'biochemistry',
    'ELECTROLYTES':  'biochemistry',
    'CRP':           'biochemistry',
    'TFT':           'biochemistry',
    'PSA':           'biochemistry',

    # Serology / Immunology
    'HIV-RAPID':     'serology',
    'HBsAg':        'serology',
    'HCV':           'serology',
    'VDRL':          'serology',
    'MALARIA-RDT':   'serology',
    'WIDAL':         'serology',
    'RF':            'serology',
    'PREGNANCY':     'serology',
    'H.P':           'serology',
    'H.P (Stool)':   'serology',
    'Typhoid':       'serology',

    # Microbiology
    'BLOOD-CS':      'microbiology',
    'SPUTUM-CS':     'microbiology',
    'URINE-CS':      'microbiology',
    'AFB':           'microbiology',

    # Urinalysis
    'URINALYSIS':    'urinalysis',

    # Parasitology
    'STOOL-EXAM':    'parasitology',

    # Other
    'SEMEN':         'other',
}


class Command(BaseCommand):
    help = 'Assign correct test categories to all lab tests'

    def handle(self, *args, **options):
        # Cache categories
        cats = {c.code: c for c in TestCategory.objects.all()}

        updated = 0
        skipped = 0
        for code, cat_code in TEST_MAP.items():
            cat = cats.get(cat_code)
            if not cat:
                self.stdout.write(self.style.ERROR(f'  Category "{cat_code}" not found – skipping {code}'))
                continue

            try:
                test = LabTest.objects.get(code=code)
            except LabTest.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  Test "{code}" not found – skipping'))
                skipped += 1
                continue

            changed = test.category != cat
            test.category = cat
            test.save(update_fields=['category'])

            # Sync the linked profile
            if test.profile:
                test.profile.category = cat
                test.profile.save(update_fields=['category'])

            tag = 'UPDATED' if changed else 'ok     '
            self.stdout.write(f'  {tag}  {test.code:20s} → {cat.name}')
            if changed:
                updated += 1

        self.stdout.write(self.style.MIGRATE_HEADING('\n── Summary ──'))
        self.stdout.write(f'  Updated : {updated}')
        self.stdout.write(f'  Skipped : {skipped}')

        # Show final distribution
        self.stdout.write(self.style.MIGRATE_HEADING('\n── Distribution ──'))
        for cat in TestCategory.objects.all():
            count = LabTest.objects.filter(category=cat).count()
            if count:
                self.stdout.write(f'  {cat.name:20s}  {count} test(s)')

        self.stdout.write(self.style.SUCCESS('\nDone.'))
