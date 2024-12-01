from django.db.models.signals import post_save
from django.dispatch import receiver
from book_catalog.models import Book
from .models import InventoryItem

@receiver(post_save, sender=Book)
def create_inventory_item(sender, instance, created, **kwargs):
    if created:
        InventoryItem.objects.create(book=instance) 