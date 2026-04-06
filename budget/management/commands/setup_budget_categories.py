from django.core.management.base import BaseCommand
from budget.models import ExpenseCategory


class Command(BaseCommand):
    help = 'Setup default expense categories for budget management'

    def handle(self, *args, **kwargs):
        categories_data = [
            {'name': 'Rent & Utilities', 'icon': 'bi-house-door', 'color': 'primary', 'description': 'Rent, electricity, water, and facility costs'},
            {'name': 'Salaries & Wages', 'icon': 'bi-people', 'color': 'success', 'description': 'Staff salaries and wages'},
            {'name': 'Medical Supplies', 'icon': 'bi-bandaid', 'color': 'danger', 'description': 'Medical equipment and supplies'},
            {'name': 'Office Supplies', 'icon': 'bi-printer', 'color': 'info', 'description': 'Stationery, printing, and office materials'},
            {'name': 'Equipment Maintenance', 'icon': 'bi-tools', 'color': 'warning', 'description': 'Equipment repairs and maintenance'},
            {'name': 'Transportation', 'icon': 'bi-truck', 'color': 'secondary', 'description': 'Fuel, vehicle maintenance, and transport'},
            {'name': 'Marketing & Advertising', 'icon': 'bi-megaphone', 'color': 'primary', 'description': 'Marketing campaigns and advertising'},
            {'name': 'Insurance', 'icon': 'bi-shield-check', 'color': 'success', 'description': 'Insurance premiums and coverage'},
            {'name': 'Training & Development', 'icon': 'bi-book', 'color': 'info', 'description': 'Staff training and professional development'},
            {'name': 'Cleaning & Janitorial', 'icon': 'bi-droplet', 'color': 'primary', 'description': 'Cleaning services and supplies'},
            {'name': 'Professional Services', 'icon': 'bi-briefcase', 'color': 'warning', 'description': 'Legal, accounting, and consulting fees'},
            {'name': 'Technology & Software', 'icon': 'bi-laptop', 'color': 'info', 'description': 'Software licenses and IT services'},
            {'name': 'Food & Beverages', 'icon': 'bi-cup-hot', 'color': 'secondary', 'description': 'Tea, coffee, and refreshments'},
            {'name': 'Security', 'icon': 'bi-lock', 'color': 'danger', 'description': 'Security services and systems'},
            {'name': 'Miscellaneous', 'icon': 'bi-three-dots', 'color': 'secondary', 'description': 'Other expenses not categorized'},
        ]
        
        created_count = 0
        updated_count = 0
        
        for cat_data in categories_data:
            category, created = ExpenseCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'icon': cat_data['icon'],
                    'color': cat_data['color'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {category.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'○ Exists: {category.name}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Setup complete!\n'
            f'- Created: {created_count} categories\n'
            f'- Already existed: {updated_count} categories\n'
            f'- Total: {ExpenseCategory.objects.count()} categories\n'
        ))
