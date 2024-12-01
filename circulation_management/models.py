from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

class CirculationRule(models.Model):
    """Defines rules for circulation like loan period, fine per day etc."""
    loan_period_days = models.PositiveIntegerField(default=14)
    max_renewals = models.PositiveIntegerField(default=2)
    fine_per_day = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    max_books_per_user = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"Circulation Rule (Loan Period: {self.loan_period_days} days)"

class BookLoan(models.Model):
    """Tracks book loans"""
    STATUS_CHOICES = [
        ('issued', 'Issued'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('lost', 'Lost'),
    ]

    user = models.ForeignKey('user_management.User', on_delete=models.CASCADE)
    book = models.ForeignKey('book_catalog.Book', on_delete=models.CASCADE) 
    issue_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    renewals = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='issued')
    fine_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    fine_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.book.title} - {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.due_date:
            rule = CirculationRule.objects.first()
            self.due_date = self.issue_date + timedelta(days=rule.loan_period_days)
        super().save(*args, **kwargs)

    def calculate_fine(self):
        if self.return_date and self.return_date > self.due_date:
            rule = CirculationRule.objects.first()
            days_overdue = (self.return_date - self.due_date).days
            self.fine_amount = Decimal(days_overdue) * rule.fine_per_day
            self.save()
        return self.fine_amount

class BookHold(models.Model):
    """Tracks hold requests for books"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey('user_management.User', on_delete=models.CASCADE)
    book = models.ForeignKey('book_catalog.Book', on_delete=models.CASCADE)
    request_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    notification_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['request_date']

    def __str__(self):
        return f"{self.book.title} - {self.user.username}" 