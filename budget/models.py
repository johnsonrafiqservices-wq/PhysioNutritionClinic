from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()


class ExpenseCategory(models.Model):
    """Categories for organizing expenses"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-tag', help_text='Bootstrap icon class')
    color = models.CharField(max_length=20, default='primary', help_text='Bootstrap color class')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Expense Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_total_expenses(self, start_date=None, end_date=None):
        """Get total expenses for this category in date range"""
        expenses = self.expenses.filter(status='approved')
        if start_date:
            expenses = expenses.filter(expense_date__gte=start_date)
        if end_date:
            expenses = expenses.filter(expense_date__lte=end_date)
        return expenses.aggregate(total=models.Sum('amount'))['total'] or Decimal('0')


class Budget(models.Model):
    """Budget planning for periods"""
    PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='monthly')
    start_date = models.DateField()
    end_date = models.DateField()
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='budgets_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"
    
    def get_allocated_amount(self):
        """Get total allocated amount from budget items"""
        return self.items.aggregate(total=models.Sum('allocated_amount'))['total'] or Decimal('0')
    
    def get_spent_amount(self):
        """Get total spent amount from approved expenses"""
        total = Decimal('0')
        for item in self.items.all():
            total += item.get_spent_amount()
        return total
    
    def get_remaining_amount(self):
        """Get remaining budget amount"""
        return self.total_amount - self.get_spent_amount()
    
    def get_utilization_percentage(self):
        """Get budget utilization percentage"""
        if self.total_amount > 0:
            return (self.get_spent_amount() / self.total_amount) * 100
        return 0


class BudgetItem(models.Model):
    """Individual line items in a budget"""
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT)
    allocated_amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category__name']
        unique_together = ['budget', 'category']
    
    def __str__(self):
        return f"{self.budget.name} - {self.category.name}"
    
    def get_spent_amount(self):
        """Get total spent for this budget item"""
        return self.expenses.filter(status='approved').aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0')
    
    def get_remaining_amount(self):
        """Get remaining amount for this budget item"""
        return self.allocated_amount - self.get_spent_amount()
    
    def get_utilization_percentage(self):
        """Get utilization percentage for this budget item"""
        if self.allocated_amount > 0:
            return (self.get_spent_amount() / self.allocated_amount) * 100
        return 0


class Expense(models.Model):
    """Individual expense records"""
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('cheque', 'Cheque'),
        ('card', 'Card'),
    ]
    
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name='expenses')
    budget_item = models.ForeignKey(BudgetItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=10, default='UGX')
    expense_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    reference_number = models.CharField(max_length=100, blank=True, help_text='Receipt/Invoice number')
    vendor_name = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    receipt_file = models.FileField(upload_to='expense_receipts/', blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='expenses_submitted')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses_approved')
    approved_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-expense_date', '-created_at']
    
    def __str__(self):
        return f"{self.category.name} - {self.amount} {self.currency} ({self.expense_date})"
    
    def approve(self, user):
        """Approve this expense"""
        self.status = 'approved'
        self.approved_by = user
        self.approved_date = timezone.now()
        self.save()
    
    def reject(self, user, reason):
        """Reject this expense"""
        self.status = 'rejected'
        self.approved_by = user
        self.approved_date = timezone.now()
        self.rejection_reason = reason
        self.save()
    
    def mark_as_paid(self):
        """Mark expense as paid"""
        if self.status == 'approved':
            self.status = 'paid'
            self.save()
