from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import (
    Medication, 
    Batch, 
    StockMovement, 
    Category, 
    Supplier,
    StockAlert
)
from branches.models import Branch

User = get_user_model()

class PharmacyModelsTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test branch
        self.branch = Branch.objects.create(
            name='Test Branch',
            address='Test Address'
        )
        
        # Create test category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Description'
        )
        
        # Create test supplier
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            contact_person='Test Contact',
            email='test@supplier.com',
            phone='1234567890',
            address='Test Address'
        )
        
        # Create test medication
        self.medication = Medication.objects.create(
            name='Test Med',
            generic_name='Test Generic',
            category=self.category,
            strength='500mg',
            form='tablet',
            reorder_level=10,
            unit_price=Decimal('10.00'),
            unit_of_measure='tablet',
            manufacturer='Test Manufacturer'
        )
        
        # Create test batch
        self.batch = Batch.objects.create(
            medication=self.medication,
            supplier=self.supplier,
            batch_number='TEST001',
            branch=self.branch,
            quantity_remaining=100,
            cost_price=Decimal('8.00'),
            selling_price=Decimal('12.00'),
            expiry_date=timezone.now().date() + timedelta(days=180),
            received_by=self.user
        )

    def test_batch_quantity_remaining(self):
        """Test that batch quantity_remaining is properly managed"""
        initial_quantity = self.batch.quantity_remaining
        
        # Test stock in movement
        stock_in = StockMovement.objects.create(
            batch=self.batch,
            movement_type='in',
            quantity=50,
            reference='Test Stock In',
            created_by=self.user
        )
        
        self.batch.refresh_from_db()
        self.assertEqual(
            self.batch.quantity_remaining, 
            initial_quantity + 50,
            "Batch quantity_remaining should increase with stock in"
        )
        
        # Test stock out movement
        stock_out = StockMovement.objects.create(
            batch=self.batch,
            movement_type='out',
            quantity=30,
            reference='Test Stock Out',
            created_by=self.user
        )
        
        self.batch.refresh_from_db()
        self.assertEqual(
            self.batch.quantity_remaining, 
            initial_quantity + 50 - 30,
            "Batch quantity_remaining should decrease with stock out"
        )
    
    def test_stock_movement_validation(self):
        """Test stock movement validation"""
        # Test invalid stock out (more than available)
        with self.assertRaises(ValueError):
            StockMovement.objects.create(
                batch=self.batch,
                movement_type='out',
                quantity=1000,  # More than available
                reference='Invalid Stock Out',
                created_by=self.user
            )
    
    def test_batch_expiry_status(self):
        """Test batch expiry status properties"""
        # Test active batch
        self.assertFalse(
            self.batch.is_expired,
            "New batch should not be expired"
        )
        
        # Test expiring soon
        soon_expiring_batch = Batch.objects.create(
            medication=self.medication,
            supplier=self.supplier,
            batch_number='TEST002',
            branch=self.branch,
            quantity_remaining=100,
            cost_price=Decimal('8.00'),
            selling_price=Decimal('12.00'),
            expiry_date=timezone.now().date() + timedelta(days=30),
            received_by=self.user
        )
        
        self.assertTrue(
            soon_expiring_batch.is_expiring_soon,
            "Batch expiring in 30 days should be marked as expiring soon"
        )
        
        # Test expired batch
        expired_batch = Batch.objects.create(
            medication=self.medication,
            supplier=self.supplier,
            batch_number='TEST003',
            branch=self.branch,
            quantity_remaining=100,
            cost_price=Decimal('8.00'),
            selling_price=Decimal('12.00'),
            expiry_date=timezone.now().date() - timedelta(days=1),
            received_by=self.user
        )
        
        self.assertTrue(
            expired_batch.is_expired,
            "Batch with past expiry date should be marked as expired"
        )