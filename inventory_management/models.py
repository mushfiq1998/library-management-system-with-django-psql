from django.db import models
from django.utils import timezone
from book_catalog.models import Book
from django.core.validators import MinValueValidator

class InventoryItem(models.Model):
    book = models.OneToOneField(
        Book, 
        on_delete=models.CASCADE,
        related_name='inventory'
    )
    total_copies = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(0)]
    )
    available_copies = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(0)]
    )
    minimum_threshold = models.PositiveIntegerField(
        default=2,
        help_text="Minimum number of copies before reordering"
    )
    last_inventory_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Inventory for {self.book.title}"
    
    def needs_reorder(self):
        return self.available_copies <= self.minimum_threshold

class InventoryLog(models.Model):
    ACTION_CHOICES = [
        ('ADD', 'Added copies'),
        ('REMOVE', 'Removed copies'),
        ('ADJUST', 'Adjusted inventory'),
        ('DAMAGE', 'Marked as damaged'),
        ('LOST', 'Marked as lost'),
        ('REPAIR', 'Sent for repair'),
        ('RETURN', 'Returned from repair'),
    ]
    
    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    quantity = models.IntegerField()
    date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(
        'user_management.User',
        on_delete=models.SET_NULL,
        null=True
    )
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.inventory_item.book.title}"

class DamagedBook(models.Model):
    STATUS_CHOICES = [
        ('DAMAGED', 'Damaged'),
        ('REPAIRING', 'Under Repair'),
        ('REPAIRED', 'Repaired'),
        ('DISCARDED', 'Discarded'),
    ]
    
    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name='damaged_copies'
    )
    damage_date = models.DateTimeField(default=timezone.now)
    damage_description = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='DAMAGED'
    )
    repair_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    repair_notes = models.TextField(blank=True)
    repaired_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Damaged copy of {self.inventory_item.book.title}" 