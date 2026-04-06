"""
Management command to create sample laboratory user accounts with different roles.

Usage:
    python manage.py create_lab_users          # create if not existing
    python manage.py create_lab_users --clear   # delete lab users first, then recreate
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

LAB_USERS = [
    {
        'username': 'lab_tech1',
        'first_name': 'Sarah',
        'last_name': 'Nakamya',
        'email': 'sarah.nakamya@excellencemedcare.com',
        'role': 'lab_technician',
        'phone': '0701000001',
        'employee_id': 'LAB-T001',
        'department': 'Laboratory',
        'password': 'LabTech@2025',
    },
    {
        'username': 'lab_tech2',
        'first_name': 'Joseph',
        'last_name': 'Okello',
        'email': 'joseph.okello@excellencemedcare.com',
        'role': 'lab_technician',
        'phone': '0701000002',
        'employee_id': 'LAB-T002',
        'department': 'Laboratory',
        'password': 'LabTech@2025',
    },
    {
        'username': 'lab_manager',
        'first_name': 'Dr. Grace',
        'last_name': 'Auma',
        'email': 'grace.auma@excellencemedcare.com',
        'role': 'lab_manager',
        'phone': '0701000003',
        'employee_id': 'LAB-M001',
        'department': 'Laboratory',
        'password': 'LabManager@2025',
    },
    {
        'username': 'pathologist',
        'first_name': 'Dr. Peter',
        'last_name': 'Ssemakula',
        'email': 'peter.ssemakula@excellencemedcare.com',
        'role': 'pathologist',
        'phone': '0701000004',
        'employee_id': 'LAB-P001',
        'department': 'Laboratory',
        'password': 'Pathologist@2025',
    },
]


class Command(BaseCommand):
    help = 'Create sample laboratory user accounts with different roles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete existing lab user accounts before creating new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            lab_roles = ['lab_technician', 'lab_manager', 'pathologist']
            deleted = User.objects.filter(role__in=lab_roles).exclude(is_superuser=True).delete()
            self.stdout.write(self.style.WARNING(f'Deleted {deleted[0]} lab user(s).'))

        created = 0
        for ud in LAB_USERS:
            if User.objects.filter(username=ud['username']).exists():
                self.stdout.write(self.style.WARNING(f'Skipped (exists): {ud["username"]}'))
                continue

            user = User.objects.create_user(
                username=ud['username'],
                password=ud['password'],
                first_name=ud['first_name'],
                last_name=ud['last_name'],
                email=ud['email'],
                role=ud['role'],
                phone=ud['phone'],
                employee_id=ud['employee_id'],
                department=ud['department'],
                is_active=True,
                is_active_employee=True,
            )
            created += 1
            self.stdout.write(self.style.SUCCESS(
                f'Created: {user.get_full_name()} ({user.username}) — {user.get_role_display()}'
            ))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS(f'Done. {created} lab user(s) created.'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')
        self.stdout.write('Lab User Credentials:')
        self.stdout.write('-' * 60)
        for ud in LAB_USERS:
            self.stdout.write(f'  {ud["role"]:20s} | {ud["username"]:15s} | {ud["password"]}')
        self.stdout.write('-' * 60)
        self.stdout.write('')
        self.stdout.write('Role Privileges:')
        self.stdout.write('  lab_technician  — Add/edit own unverified results')
        self.stdout.write('  lab_manager     — Full access: add/edit/delete/verify results, manage tests')
        self.stdout.write('  pathologist     — Add/edit/verify results, read-only patients')
