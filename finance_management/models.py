from django.db import models
from django.conf import settings
from decimal import Decimal

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]
    
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('ONLINE', 'Online'),
        ('BANK_TRANSFER', 'Bank Transfer'),
    ]
    
    CATEGORIES = [
        ('FINE', 'Library Fine'),
        ('MEMBERSHIP', 'Membership Fee'),
        ('SALARY', 'Staff Salary'),
        ('MAINTENANCE', 'Maintenance'),
        ('BOOKS', 'Book Purchase'),
        ('UTILITIES', 'Utilities'),
        ('OTHER', 'Other'),
    ]

    transaction_id = models.CharField(max_length=20, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHODS)
    description = models.TextField()
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='COMPLETED')
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            prefix = 'INC' if self.type == 'INCOME' else 'EXP'
            last_transaction = Transaction.objects.filter(type=self.type).order_by('-id').first()
            if last_transaction:
                last_number = int(last_transaction.transaction_id[3:])
                new_number = last_number + 1
            else:
                new_number = 1
            self.transaction_id = f"{prefix}{new_number:07d}"
        super().save(*args, **kwargs)

class Income(models.Model):
    INCOME_CATEGORIES = [
        ('FINE', 'Library Fine'),
        ('MEMBERSHIP', 'Membership Fee'),
        ('DONATION', 'Donation'),
        ('LATE_FEE', 'Late Return Fee'),
        ('PRINTING', 'Printing Service'),
        ('OTHER', 'Other'),
    ]

    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('ONLINE', 'Online'),
        ('BANK_TRANSFER', 'Bank Transfer'),
    ]

    income_id = models.CharField(max_length=20, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=20, choices=INCOME_CATEGORIES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHODS)
    description = models.TextField()
    received_from = models.CharField(max_length=100)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='COMPLETED')

    def save(self, *args, **kwargs):
        if not self.income_id:
            last_income = Income.objects.order_by('-id').first()
            if last_income:
                last_number = int(last_income.income_id[3:])
                new_number = last_number + 1
            else:
                new_number = 1
            self.income_id = f"INC{new_number:07d}"
        super().save(*args, **kwargs)

class Expense(models.Model):
    EXPENSE_CATEGORIES = [
        ('SALARY', 'Staff Salary'),
        ('MAINTENANCE', 'Maintenance'),
        ('BOOKS', 'Book Purchase'),
        ('UTILITIES', 'Utilities'),
        ('SUPPLIES', 'Office Supplies'),
        ('EQUIPMENT', 'Equipment'),
        ('SOFTWARE', 'Software/Digital Resources'),
        ('OTHER', 'Other'),
    ]

    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CHECK', 'Check'),
    ]

    expense_id = models.CharField(max_length=20, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=20, choices=EXPENSE_CATEGORIES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHODS)
    description = models.TextField()
    paid_to = models.CharField(max_length=100)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='COMPLETED')

    def save(self, *args, **kwargs):
        if not self.expense_id:
            last_expense = Expense.objects.order_by('-id').first()
            if last_expense:
                last_number = int(last_expense.expense_id[3:])
                new_number = last_number + 1
            else:
                new_number = 1
            self.expense_id = f"EXP{new_number:07d}"
        super().save(*args, **kwargs)

class Fine(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    date_issued = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    paid = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True)

class Payment(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    payer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    receipt_number = models.CharField(max_length=20, unique=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            last_payment = Payment.objects.order_by('-id').first()
            if last_payment:
                last_number = int(last_payment.receipt_number[3:])
                new_number = last_number + 1
            else:
                new_number = 1
            self.receipt_number = f"RCP{new_number:07d}"
        super().save(*args, **kwargs) 