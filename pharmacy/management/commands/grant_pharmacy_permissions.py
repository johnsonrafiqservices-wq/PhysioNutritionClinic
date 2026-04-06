from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from pharmacy.models import StockMovement, Medication, Batch, Category, Supplier

User = get_user_model()

class Command(BaseCommand):
    help = 'Grant all pharmacy permissions to admin users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username to grant permissions to (default: all admin users)',
        )

    def handle(self, *args, **options):
        username = options.get('username')
        
        # Get users
        if username:
            users = User.objects.filter(username=username)
            if not users.exists():
                self.stdout.write(self.style.ERROR(f'User "{username}" not found'))
                return
        else:
            users = User.objects.filter(is_staff=True) | User.objects.filter(role='admin')
        
        # Get all pharmacy permissions
        pharmacy_models = [StockMovement, Medication, Batch, Category, Supplier]
        permissions = []
        
        for model in pharmacy_models:
            content_type = ContentType.objects.get_for_model(model)
            model_permissions = Permission.objects.filter(content_type=content_type)
            permissions.extend(model_permissions)
        
        # Grant permissions to users
        for user in users:
            user.user_permissions.add(*permissions)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Granted {len(permissions)} pharmacy permissions to {user.username}'
                )
            )
        
        self.stdout.write(self.style.SUCCESS('Done!'))
