from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal

from django.contrib.auth import get_user_model
from budget.models import ExpenseCategory, Budget, BudgetItem, Expense


class Command(BaseCommand):
    help = "Create sample budget, categories, and expenses for demo/testing.\n\n" \
           "Safe to run multiple times; it will not duplicate data if it already exists."

    def handle(self, *args, **options):
        User = get_user_model()

        # Use first superuser or any user as creator/submitter
        user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not user:
            self.stderr.write(self.style.ERROR("No users found. Create a user first."))
            return

        self.stdout.write(self.style.WARNING(f"Using user '{user.username}' as creator of sample data."))

        # 1) Create expense categories
        category_defs = [
            ("Salaries", "Staff salaries and allowances", "bi-people", "primary"),
            ("Rent", "Clinic building rent", "bi-house", "info"),
            ("Utilities", "Electricity, water, internet", "bi-lightning", "warning"),
            ("Supplies", "Medical and office supplies", "bi-box", "success"),
            ("Maintenance", "Repairs and maintenance", "bi-tools", "danger"),
        ]

        categories = {}
        for name, desc, icon, color in category_defs:
            cat, created = ExpenseCategory.objects.get_or_create(
                name=name,
                defaults={
                    "description": desc,
                    "icon": icon,
                    "color": color,
                    "is_active": True,
                },
            )
            categories[name] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category: {name}"))

        # 2) Create a current-month budget
        today = timezone.now().date()
        start_date = today.replace(day=1)
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1, day=31)
        else:
            # approximate end of month as 30th for demo purposes
            end_date = start_date.replace(day=28) + timezone.timedelta(days=3)

        budget, created = Budget.objects.get_or_create(
            name=f"Monthly Budget {start_date.strftime('%b %Y')}",
            start_date=start_date,
            end_date=end_date,
            defaults={
                "description": "Sample monthly operational budget for demonstration.",
                "period_type": "monthly",
                "total_amount": Decimal("20000000.00"),
                "status": "active",
                "created_by": user,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created budget: {budget.name}"))
        else:
            self.stdout.write(self.style.WARNING(f"Using existing budget: {budget.name}"))

        # 3) Create budget items
        item_defs = [
            ("Salaries", "Salaries for clinical and admin staff", "8000000.00"),
            ("Rent", "Clinic premises rent", "4000000.00"),
            ("Utilities", "Electricity, water, internet", "1500000.00"),
            ("Supplies", "Drugs, consumables, stationery", "3000000.00"),
            ("Maintenance", "Repairs and servicing", "1500000.00"),
        ]

        budget_items = {}
        for cat_name, notes, amount in item_defs:
            category = categories.get(cat_name)
            if not category:
                continue
            item, created = BudgetItem.objects.get_or_create(
                budget=budget,
                category=category,
                defaults={
                    "allocated_amount": Decimal(amount),
                    "notes": notes,
                },
            )
            budget_items[cat_name] = item
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created budget item: {budget.name} - {cat_name}"))

        # 4) Create sample expenses
        # Only create if there are no expenses yet for this budget period
        existing_expenses = Expense.objects.filter(
            expense_date__gte=start_date,
            expense_date__lte=end_date,
        ).exists()
        if existing_expenses:
            self.stdout.write(self.style.WARNING("Expenses already exist for this period; not adding duplicates."))
            return

        expense_defs = [
            ("Salaries", "November staff salaries", "7500000.00", "bank_transfer", "EMC-PAY-001", "Staff Payroll"),
            ("Rent", "Clinic rent payment", "4000000.00", "bank_transfer", "EMC-RENT-001", "Landlord Ltd"),
            ("Utilities", "Electricity and water bills", "1200000.00", "mobile_money", "EMC-UTIL-001", "UMEME / NWSC"),
            ("Supplies", "Medical consumables restock", "2200000.00", "cash", "EMC-SUP-001", "MedSupplies Co"),
            ("Maintenance", "Generator service", "800000.00", "cash", "EMC-MTN-001", "TechMaintain Ltd"),
        ]

        for cat_name, desc, amount, method, ref, vendor in expense_defs:
            category = categories.get(cat_name)
            budget_item = budget_items.get(cat_name)
            if not category:
                continue
            Expense.objects.create(
                category=category,
                budget_item=budget_item,
                description=desc,
                amount=Decimal(amount),
                currency="UGX",
                expense_date=today,
                payment_method=method,
                reference_number=ref,
                vendor_name=vendor,
                status="approved",
                submitted_by=user,
                approved_by=user,
                approved_date=timezone.now(),
            )
            self.stdout.write(self.style.SUCCESS(f"Created expense: {cat_name} - {amount}"))

        self.stdout.write(self.style.SUCCESS("Sample budget and expenses created successfully."))
