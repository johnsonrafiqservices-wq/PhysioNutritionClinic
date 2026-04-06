"""
Management command to populate sample lab test requests and results
"""
import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from laboratory.models import LabTest, LabTestRequest, LabTestResult
from patients.models import Patient

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate sample lab test requests and results'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of lab requests to create (default: 50)'
        )

    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(self.style.WARNING(f'Creating {count} sample lab test requests and results...'))

        # Get or create lab tests
        lab_tests = self.create_lab_tests()
        
        # Get patients and staff
        patients = list(Patient.objects.all()[:30])  # Use first 30 patients
        if not patients:
            self.stdout.write(self.style.ERROR('No patients found. Please create patients first.'))
            return
        
        staff = list(User.objects.filter(is_staff=True))
        if not staff:
            self.stdout.write(self.style.ERROR('No staff users found.'))
            return

        # Create lab requests and results
        created_requests = 0
        created_results = 0

        for i in range(count):
            # Random patient and test
            patient = random.choice(patients)
            test = random.choice(lab_tests)
            requested_by = random.choice(staff)
            
            # Random date within last 60 days
            days_ago = random.randint(0, 60)
            date_requested = timezone.now() - timedelta(days=days_ago)
            
            # Sample collection (70% of requests have sample collected)
            sample_collected = random.random() > 0.3
            sample_collected_at = date_requested + timedelta(hours=random.randint(1, 4)) if sample_collected else None
            
            # Determine status based on sample collection
            if sample_collected_at:
                status = random.choice(['sample_collected', 'in_progress', 'completed'])
            else:
                status = 'requested'
            
            # Create lab request
            lab_request = LabTestRequest.objects.create(
                patient=patient,
                test=test,
                requested_by=requested_by,
                date_requested=date_requested,
                priority=random.choice(['routine', 'urgent', 'stat']),
                clinical_notes=self.get_clinical_notes(),
                sample_collected_at=sample_collected_at,
                status=status
            )
            created_requests += 1

            # Create result for 80% of requests that have samples collected
            if random.random() > 0.2 and sample_collected_at:
                result_value, is_abnormal = self.get_test_result(test.name)
                
                # Get unit from test or default
                result_unit = self.get_default_unit(test.name)
                if hasattr(test, 'unit') and test.unit:
                    result_unit = test.unit
                
                lab_result = LabTestResult.objects.create(
                    request=lab_request,
                    result_value=result_value,
                    result_unit=result_unit,
                    is_abnormal=is_abnormal,
                    reported_by=random.choice(staff),
                    verified_by=random.choice(staff) if random.random() > 0.3 else None,
                    verified=random.choice([True, False]),
                    date_reported=sample_collected_at + timedelta(hours=random.randint(4, 24)),
                    interpretation=self.get_interpretation(test.name, is_abnormal),
                    remarks=self.get_remarks() if random.random() > 0.7 else None
                )
                created_results += 1
                
                # Update request status to completed if result exists
                lab_request.status = 'completed'
                lab_request.save()

        self.stdout.write(self.style.SUCCESS(f'✓ Created {created_requests} lab requests'))
        self.stdout.write(self.style.SUCCESS(f'✓ Created {created_results} lab results'))
        self.stdout.write(self.style.SUCCESS('Lab data population completed!'))

    def create_lab_tests(self):
        """Create or get common lab tests"""
        tests_data = [
            # Hematology
            {
                'name': 'Complete Blood Count (CBC)',
                'code': 'CBC',
                'category': 'hematology',
                'price': Decimal('25000'),
                'normal_range': '13.0-17.0 g/dL',
                'sample_type': 'Blood'
            },
            {
                'name': 'Hemoglobin',
                'code': 'HGB',
                'category': 'hematology',
                'price': Decimal('15000'),
                'normal_range': '12.0-16.0 g/dL',
                'sample_type': 'Blood'
            },
            {
                'name': 'White Blood Cell Count',
                'code': 'WBC',
                'category': 'hematology',
                'price': Decimal('15000'),
                'normal_range': '4.5-11.0 x10^3/μL',
                'sample_type': 'Blood'
            },
            {
                'name': 'Platelet Count',
                'code': 'PLT',
                'category': 'hematology',
                'price': Decimal('15000'),
                'normal_range': '150-400 x10^3/μL',
                'sample_type': 'Blood'
            },
            # Chemistry
            {
                'name': 'Blood Glucose (Fasting)',
                'code': 'FBS',
                'category': 'biochemistry',
                'price': Decimal('10000'),
                'normal_range': '70-100 mg/dL',
                'sample_type': 'Blood'
            },
            {
                'name': 'Blood Glucose (Random)',
                'code': 'RBS',
                'category': 'biochemistry',
                'price': Decimal('10000'),
                'normal_range': '70-140 mg/dL',
                'sample_type': 'Blood'
            },
            {
                'name': 'HbA1c',
                'code': 'HBA1C',
                'category': 'biochemistry',
                'price': Decimal('35000'),
                'normal_range': '4.0-5.6 %',
                'sample_type': 'Blood'
            },
            {
                'name': 'Creatinine',
                'code': 'CREAT',
                'category': 'biochemistry',
                'price': Decimal('15000'),
                'normal_range': '0.7-1.3 mg/dL',
                'sample_type': 'Blood'
            },
            {
                'name': 'Blood Urea Nitrogen (BUN)',
                'code': 'BUN',
                'category': 'biochemistry',
                'price': Decimal('15000'),
                'normal_range': '7-20 mg/dL',
                'sample_type': 'Blood'
            },
            {
                'name': 'Total Cholesterol',
                'code': 'CHOL',
                'category': 'biochemistry',
                'price': Decimal('20000'),
                'normal_range': '<200 mg/dL',
                'sample_type': 'Blood'
            },
            {
                'name': 'HDL Cholesterol',
                'code': 'HDL',
                'category': 'biochemistry',
                'price': Decimal('20000'),
                'normal_range': '>40 mg/dL',
                'sample_type': 'Blood'
            },
            {
                'name': 'LDL Cholesterol',
                'code': 'LDL',
                'category': 'biochemistry',
                'price': Decimal('20000'),
                'normal_range': '<100 mg/dL',
                'sample_type': 'Blood'
            },
            {
                'name': 'Triglycerides',
                'code': 'TRIG',
                'category': 'biochemistry',
                'price': Decimal('20000'),
                'normal_range': '<150 mg/dL',
                'sample_type': 'Blood'
            },
            # Liver Function
            {
                'name': 'ALT (SGPT)',
                'code': 'ALT',
                'category': 'biochemistry',
                'price': Decimal('18000'),
                'normal_range': '7-55 U/L',
                'sample_type': 'Blood'
            },
            {
                'name': 'AST (SGOT)',
                'code': 'AST',
                'category': 'biochemistry',
                'price': Decimal('18000'),
                'normal_range': '8-48 U/L',
                'sample_type': 'Blood'
            },
            # Serology
            {
                'name': 'Malaria Rapid Test',
                'code': 'MRDT',
                'category': 'serology',
                'price': Decimal('8000'),
                'normal_range': 'Negative',
                'sample_type': 'Blood'
            },
            {
                'name': 'HIV Test',
                'code': 'HIV',
                'category': 'serology',
                'price': Decimal('15000'),
                'normal_range': 'Non-reactive',
                'sample_type': 'Blood'
            },
            {
                'name': 'Hepatitis B Surface Antigen',
                'code': 'HBSAG',
                'category': 'serology',
                'price': Decimal('25000'),
                'normal_range': 'Non-reactive',
                'sample_type': 'Blood'
            },
            # Microbiology
            {
                'name': 'Urinalysis (Complete)',
                'code': 'UA',
                'category': 'microbiology',
                'price': Decimal('12000'),
                'normal_range': 'Normal',
                'sample_type': 'Urine'
            },
            {
                'name': 'Urine Pregnancy Test',
                'code': 'UPT',
                'category': 'serology',
                'price': Decimal('5000'),
                'normal_range': 'Negative',
                'sample_type': 'Urine'
            },
        ]

        created_tests = []
        for test_data in tests_data:
            test, created = LabTest.objects.get_or_create(
                code=test_data['code'],
                defaults=test_data
            )
            created_tests.append(test)
            if created:
                self.stdout.write(f'  Created test: {test.name}')

        return created_tests

    def get_test_result(self, test_name):
        """Generate realistic test results with some abnormal values"""
        results = {
            'Complete Blood Count (CBC)': (
                lambda: (f"{random.uniform(11.0, 18.0):.1f}", random.random() > 0.7)
            ),
            'Hemoglobin': (
                lambda: (f"{random.uniform(10.0, 17.0):.1f}", random.random() > 0.7)
            ),
            'White Blood Cell Count': (
                lambda: (f"{random.uniform(3.5, 13.0):.1f}", random.random() > 0.7)
            ),
            'Platelet Count': (
                lambda: (f"{random.randint(120, 450)}", random.random() > 0.8)
            ),
            'Blood Glucose (Fasting)': (
                lambda: (f"{random.randint(65, 150)}", random.random() > 0.6)
            ),
            'Blood Glucose (Random)': (
                lambda: (f"{random.randint(70, 200)}", random.random() > 0.6)
            ),
            'HbA1c': (
                lambda: (f"{random.uniform(4.0, 8.5):.1f}", random.random() > 0.7)
            ),
            'Creatinine': (
                lambda: (f"{random.uniform(0.6, 1.8):.1f}", random.random() > 0.75)
            ),
            'Blood Urea Nitrogen (BUN)': (
                lambda: (f"{random.randint(5, 35)}", random.random() > 0.75)
            ),
            'Total Cholesterol': (
                lambda: (f"{random.randint(140, 280)}", random.random() > 0.5)
            ),
            'HDL Cholesterol': (
                lambda: (f"{random.randint(30, 70)}", random.random() > 0.6)
            ),
            'LDL Cholesterol': (
                lambda: (f"{random.randint(70, 180)}", random.random() > 0.5)
            ),
            'Triglycerides': (
                lambda: (f"{random.randint(80, 250)}", random.random() > 0.5)
            ),
            'ALT (SGPT)': (
                lambda: (f"{random.randint(10, 120)}", random.random() > 0.7)
            ),
            'AST (SGOT)': (
                lambda: (f"{random.randint(10, 100)}", random.random() > 0.7)
            ),
            'Malaria Rapid Test': (
                lambda: (random.choice(['Negative', 'Positive']), random.random() > 0.85)
            ),
            'HIV Test': (
                lambda: (random.choice(['Non-reactive', 'Reactive']), random.random() > 0.95)
            ),
            'Hepatitis B Surface Antigen': (
                lambda: (random.choice(['Non-reactive', 'Reactive']), random.random() > 0.9)
            ),
            'Urinalysis (Complete)': (
                lambda: (random.choice(['Normal', 'Abnormal']), random.random() > 0.8)
            ),
            'Urine Pregnancy Test': (
                lambda: (random.choice(['Negative', 'Positive']), random.random() > 0.7)
            ),
        }

        generator = results.get(test_name, lambda: (f"{random.uniform(1.0, 10.0):.1f}", False))
        return generator()

    def get_default_unit(self, test_name):
        """Get default unit for test"""
        units = {
            'Complete Blood Count (CBC)': 'g/dL',
            'Hemoglobin': 'g/dL',
            'White Blood Cell Count': '10^3/μL',
            'Platelet Count': '10^3/μL',
            'Blood Glucose (Fasting)': 'mg/dL',
            'Blood Glucose (Random)': 'mg/dL',
            'HbA1c': '%',
            'Creatinine': 'mg/dL',
            'Blood Urea Nitrogen (BUN)': 'mg/dL',
            'Total Cholesterol': 'mg/dL',
            'HDL Cholesterol': 'mg/dL',
            'LDL Cholesterol': 'mg/dL',
            'Triglycerides': 'mg/dL',
            'ALT (SGPT)': 'U/L',
            'AST (SGOT)': 'U/L',
            'Malaria Rapid Test': 'Qualitative',
            'HIV Test': 'Qualitative',
            'Hepatitis B Surface Antigen': 'Qualitative',
            'Urinalysis (Complete)': 'Various',
            'Urine Pregnancy Test': 'Qualitative',
        }
        return units.get(test_name, 'Unit')

    def get_clinical_notes(self):
        """Get random clinical notes"""
        notes = [
            'Patient presents with symptoms of anemia',
            'Follow-up test for diabetes management',
            'Pre-operative workup',
            'Routine health screening',
            'Patient complains of fatigue and weakness',
            'Suspected kidney dysfunction',
            'Cardiovascular risk assessment',
            'Patient with history of hypertension',
            'Liver function monitoring',
            'Fever investigation',
            'Weight loss and malaise',
            'Annual physical examination',
            'Pre-employment medical',
            'Insurance medical examination',
            'Suspected malaria',
        ]
        return random.choice(notes)

    def get_interpretation(self, test_name, is_abnormal):
        """Get interpretation based on test and abnormality"""
        if not is_abnormal:
            return 'Results within normal limits. No immediate action required.'
        
        interpretations = {
            'Complete Blood Count (CBC)': 'Abnormal values detected. Further investigation recommended.',
            'Hemoglobin': 'Hemoglobin level outside normal range. Suggest iron studies.',
            'Blood Glucose (Fasting)': 'Elevated glucose levels. Recommend HbA1c test and dietary counseling.',
            'Blood Glucose (Random)': 'Glucose level abnormal. Follow-up with fasting glucose test.',
            'HbA1c': 'Elevated HbA1c indicating poor glycemic control. Adjust diabetes management.',
            'Creatinine': 'Elevated creatinine suggests possible renal impairment. Monitor kidney function.',
            'Total Cholesterol': 'Elevated cholesterol. Recommend lipid-lowering therapy and lifestyle modification.',
            'ALT (SGPT)': 'Elevated liver enzymes. Investigate for hepatic pathology.',
            'Malaria Rapid Test': 'Positive for malaria. Initiate antimalarial treatment immediately.',
            'HIV Test': 'Reactive test. Confirmatory testing required with counseling.',
        }
        
        return interpretations.get(test_name, 'Abnormal result detected. Clinical correlation recommended.')

    def get_remarks(self):
        """Get additional remarks"""
        remarks = [
            'Sample received in good condition',
            'Repeat test if clinical suspicion persists',
            'Correlate with clinical findings',
            'Patient was fasting',
            'Patient was not fasting',
            'Sample slightly hemolyzed',
            'Results validated and verified',
            'Quality control passed',
        ]
        return random.choice(remarks)
