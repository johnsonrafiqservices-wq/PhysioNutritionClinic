"""
Seed comprehensive budgets, expenses, and pharmacy sales for demo/testing.
Safe to run multiple times — uses get_or_create where possible and checks
for existing sales before creating duplicates.

Usage:  python manage.py seed_full_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import timedelta, date
import random

User = get_user_model()


class Command(BaseCommand):
    help = "Seed budgets, expenses (with categories), and pharmacy sales data."

    def handle(self, *args, **options):
        user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not user:
            self.stderr.write(self.style.ERROR("No users in DB. Create a user first."))
            return

        self.stdout.write(self.style.WARNING(f"Using user: {user.username}"))
        self._seed_categories()
        self._seed_budgets(user)
        self._seed_expenses(user)
        self._seed_pharmacy_sales(user)
        self.stdout.write(self.style.SUCCESS("\nAll done — budgets, expenses & sales seeded."))

    # ------------------------------------------------------------------
    # Expense categories
    # ------------------------------------------------------------------
    CATEGORY_DEFS = [
        ("Salaries & Wages", "Staff salaries, wages, allowances", "bi-people-fill", "primary"),
        ("Rent & Lease", "Building rent and lease payments", "bi-house-fill", "info"),
        ("Utilities", "Electricity, water, internet, phone", "bi-lightning-fill", "warning"),
        ("Medical Supplies", "Drugs, disposables, lab reagents", "bi-capsule", "success"),
        ("Office Supplies", "Stationery, toner, printing", "bi-printer", "secondary"),
        ("Maintenance & Repairs", "Equipment servicing, building repairs", "bi-tools", "danger"),
        ("Transport & Fuel", "Staff travel, ambulance fuel, courier", "bi-truck", "dark"),
        ("Insurance", "Property, liability, health insurance", "bi-shield-check", "primary"),
        ("Marketing", "Advertising, community outreach", "bi-megaphone", "info"),
        ("Professional Fees", "Legal, audit, consulting", "bi-briefcase", "warning"),
        ("Training & Development", "Staff CPD, workshops, conferences", "bi-mortarboard", "success"),
        ("IT & Software", "Licenses, hosting, hardware", "bi-pc-display", "danger"),
    ]

    def _seed_categories(self):
        from budget.models import ExpenseCategory
        self.categories = {}
        for name, desc, icon, color in self.CATEGORY_DEFS:
            cat, created = ExpenseCategory.objects.get_or_create(
                name=name,
                defaults={"description": desc, "icon": icon, "color": color, "is_active": True},
            )
            self.categories[name] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f"  + Category: {name}"))

    # ------------------------------------------------------------------
    # Budgets & budget items
    # ------------------------------------------------------------------
    def _seed_budgets(self, user):
        from budget.models import Budget, BudgetItem

        today = timezone.now().date()

        budgets_defs = [
            {
                "name": f"Monthly Budget — {today.strftime('%B %Y')}",
                "period_type": "monthly",
                "start": today.replace(day=1),
                "end": (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1),
                "total": Decimal("25000000"),
                "status": "active",
                "items": {
                    "Salaries & Wages": Decimal("10000000"),
                    "Rent & Lease": Decimal("4000000"),
                    "Utilities": Decimal("1500000"),
                    "Medical Supplies": Decimal("4000000"),
                    "Maintenance & Repairs": Decimal("1500000"),
                    "Office Supplies": Decimal("500000"),
                    "Transport & Fuel": Decimal("1000000"),
                    "IT & Software": Decimal("500000"),
                    "Training & Development": Decimal("500000"),
                    "Marketing": Decimal("500000"),
                    "Insurance": Decimal("500000"),
                    "Professional Fees": Decimal("500000"),
                },
            },
            {
                "name": f"Q1 {today.year} Operating Budget",
                "period_type": "quarterly",
                "start": date(today.year, 1, 1),
                "end": date(today.year, 3, 31),
                "total": Decimal("75000000"),
                "status": "active",
                "items": {
                    "Salaries & Wages": Decimal("30000000"),
                    "Rent & Lease": Decimal("12000000"),
                    "Utilities": Decimal("4500000"),
                    "Medical Supplies": Decimal("12000000"),
                    "Maintenance & Repairs": Decimal("4500000"),
                    "Office Supplies": Decimal("1500000"),
                    "Transport & Fuel": Decimal("3000000"),
                    "Insurance": Decimal("1500000"),
                    "Marketing": Decimal("1500000"),
                    "Professional Fees": Decimal("1500000"),
                    "Training & Development": Decimal("1500000"),
                    "IT & Software": Decimal("1500000"),
                },
            },
        ]

        self.budget_items_map = {}  # category_name -> BudgetItem (for linking expenses)

        for bdef in budgets_defs:
            budget, created = Budget.objects.get_or_create(
                name=bdef["name"],
                start_date=bdef["start"],
                end_date=bdef["end"],
                defaults={
                    "description": f"Auto-seeded {bdef['period_type']} budget.",
                    "period_type": bdef["period_type"],
                    "total_amount": bdef["total"],
                    "status": bdef["status"],
                    "created_by": user,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  + Budget: {budget.name}"))
            else:
                self.stdout.write(f"  = Budget exists: {budget.name}")

            for cat_name, amount in bdef["items"].items():
                cat = self.categories.get(cat_name)
                if not cat:
                    continue
                item, ic = BudgetItem.objects.get_or_create(
                    budget=budget,
                    category=cat,
                    defaults={"allocated_amount": amount, "notes": f"Allocated for {cat_name}"},
                )
                # Keep the most recent budget's items for expense linking
                if budget.status == "active":
                    self.budget_items_map[cat_name] = item
                if ic:
                    self.stdout.write(f"    + Item: {cat_name} → {amount:,.0f}")

    # ------------------------------------------------------------------
    # Expenses  (spread over last 60 days, various statuses/vendors)
    # ------------------------------------------------------------------
    VENDORS = [
        "MedSupplies Uganda Ltd", "UMEME", "National Water & Sewerage Corp",
        "Stationery World", "TechFix Solutions", "SafeGuard Insurance",
        "City Pharmacy Distributors", "Express Courier Services",
        "Digital Health Systems", "ProAudit & Associates",
        "CleanCare Maintenance", "TotalEnergies", "MTN Business",
        "Kampala Printers", "LabReagents East Africa",
    ]

    def _seed_expenses(self, user):
        from budget.models import Expense

        today = timezone.now().date()
        # Only add if fewer than 20 expenses exist in last 60 days
        recent = Expense.objects.filter(expense_date__gte=today - timedelta(days=60)).count()
        if recent >= 30:
            self.stdout.write(self.style.WARNING(
                f"  Already {recent} expenses in last 60 days — skipping expense seed."
            ))
            return

        random.seed(42)  # reproducible

        methods = ["cash", "bank_transfer", "mobile_money", "cheque", "card"]
        statuses_weights = [("approved", 50), ("paid", 25), ("pending", 15), ("rejected", 10)]
        statuses = [s for s, w in statuses_weights for _ in range(w)]

        expense_templates = [
            ("Salaries & Wages", "Staff salary payment — {month}", (7000000, 10000000)),
            ("Rent & Lease", "Monthly clinic rent", (3500000, 4000000)),
            ("Utilities", "Electricity bill — {month}", (400000, 700000)),
            ("Utilities", "Water bill — {month}", (150000, 300000)),
            ("Utilities", "Internet service — {month}", (200000, 350000)),
            ("Medical Supplies", "Drug restock — antiobiotics", (800000, 2000000)),
            ("Medical Supplies", "Lab reagents purchase", (500000, 1500000)),
            ("Medical Supplies", "Disposable gloves & syringes", (200000, 600000)),
            ("Office Supplies", "Printer toner & paper", (80000, 200000)),
            ("Office Supplies", "Receipt books & folders", (50000, 120000)),
            ("Maintenance & Repairs", "Generator servicing", (300000, 800000)),
            ("Maintenance & Repairs", "Plumbing repairs", (100000, 350000)),
            ("Transport & Fuel", "Ambulance fuel", (200000, 500000)),
            ("Transport & Fuel", "Staff travel allowance", (150000, 400000)),
            ("Insurance", "Monthly insurance premium", (400000, 500000)),
            ("Marketing", "Social media ads — {month}", (100000, 300000)),
            ("Marketing", "Community health outreach", (200000, 500000)),
            ("Professional Fees", "Monthly legal retainer", (300000, 500000)),
            ("Training & Development", "First-aid refresher course", (200000, 600000)),
            ("IT & Software", "EMR hosting & licenses", (150000, 350000)),
            ("IT & Software", "Laptop repair", (100000, 300000)),
            ("Medical Supplies", "PPE restock", (300000, 700000)),
            ("Maintenance & Repairs", "AC unit service", (150000, 400000)),
            ("Salaries & Wages", "Overtime allowances", (500000, 1500000)),
            ("Transport & Fuel", "Courier service", (50000, 150000)),
        ]

        count = 0
        for days_ago in range(60, -1, -1):
            # 0-3 expenses per day
            n_expenses = random.choices([0, 1, 2, 3], weights=[20, 40, 30, 10])[0]
            exp_date = today - timedelta(days=days_ago)
            month_label = exp_date.strftime("%B %Y")

            for _ in range(n_expenses):
                tpl = random.choice(expense_templates)
                cat_name, desc_tpl, (lo, hi) = tpl
                cat = self.categories.get(cat_name)
                if not cat:
                    continue
                amount = Decimal(str(random.randint(lo, hi)))
                status = random.choice(statuses)
                method = random.choice(methods)
                vendor = random.choice(self.VENDORS)
                budget_item = self.budget_items_map.get(cat_name)

                desc = desc_tpl.replace("{month}", month_label)

                exp = Expense.objects.create(
                    category=cat,
                    budget_item=budget_item,
                    description=desc,
                    amount=amount,
                    currency="UGX",
                    expense_date=exp_date,
                    payment_method=method,
                    reference_number=f"EMC-{cat_name[:3].upper()}-{random.randint(1000,9999)}",
                    vendor_name=vendor,
                    status=status,
                    submitted_by=user,
                    approved_by=user if status in ("approved", "paid") else None,
                    approved_date=timezone.now() if status in ("approved", "paid") else None,
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"  + Created {count} expenses across 60 days"))

    # ------------------------------------------------------------------
    # Pharmacy sales  (StockMovement type=out, ref contains SALE)
    # ------------------------------------------------------------------
    def _seed_pharmacy_sales(self, user):
        from pharmacy.models import Batch, StockMovement

        # Only add if fewer than 20 sale movements exist
        existing_sales = StockMovement.objects.filter(
            movement_type="out", reference__icontains="SALE"
        ).count()
        if existing_sales >= 30:
            self.stdout.write(self.style.WARNING(
                f"  Already {existing_sales} sale records — skipping sales seed."
            ))
            return

        batches = list(
            Batch.objects.filter(
                is_active=True, quantity_remaining__gt=5,
                expiry_date__gt=timezone.now().date(),
            ).select_related("medication")[:30]
        )
        if not batches:
            self.stdout.write(self.style.WARNING("  No active batches with stock — skipping sales."))
            return

        random.seed(123)
        today = timezone.now().date()
        sale_count = 0

        for days_ago in range(30, -1, -1):
            sale_date = today - timedelta(days=days_ago)
            # 1-5 sales per day
            n_sales = random.randint(1, 5)
            for _ in range(n_sales):
                batch = random.choice(batches)
                max_qty = min(batch.quantity_remaining, 10)
                if max_qty < 1:
                    continue
                qty = random.randint(1, max_qty)
                ref = f"SALE-{sale_date.strftime('%Y%m%d')}-{random.randint(100,999)}"

                StockMovement.objects.create(
                    batch=batch,
                    movement_type="out",
                    quantity=qty,
                    reference=ref,
                    notes=f"Over-the-counter sale",
                    created_by=user,
                )
                # Reduce batch stock
                batch.quantity_remaining -= qty
                batch.save(update_fields=["quantity_remaining"])
                sale_count += 1

        self.stdout.write(self.style.SUCCESS(f"  + Created {sale_count} pharmacy sale records across 30 days"))
