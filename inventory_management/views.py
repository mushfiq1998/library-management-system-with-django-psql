from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, F
from .models import InventoryItem, InventoryLog, DamagedBook
from .forms import InventoryItemForm, InventoryAdjustmentForm, DamagedBookForm
from book_catalog.models import Book

def is_staff(user):
    return user.role in ['ADMIN', 'LIBRARIAN']

@login_required
@user_passes_test(is_staff)
def inventory_list(request):
    query = request.GET.get('search', '')
    filter_status = request.GET.get('status', '')
    
    inventory_items = InventoryItem.objects.all()
    
    if query:
        inventory_items = inventory_items.filter(
            Q(book__title__icontains=query) |
            Q(book__isbn__icontains=query)
        )
    
    if filter_status == 'low':
        inventory_items = inventory_items.filter(
            available_copies__lte=F('minimum_threshold')
        )
    elif filter_status == 'out':
        inventory_items = inventory_items.filter(available_copies=0)
    
    context = {
        'inventory_items': inventory_items,
        'search_query': query,
        'filter_status': filter_status
    }
    return render(request, 'inventory_management/inventory_list.html', context)

@login_required
@user_passes_test(is_staff)
def inventory_detail(request, pk):
    inventory_item = get_object_or_404(InventoryItem, pk=pk)
    logs = inventory_item.logs.all().order_by('-date')
    damaged_books = inventory_item.damaged_copies.all().order_by('-damage_date')
    
    context = {
        'inventory_item': inventory_item,
        'logs': logs,
        'damaged_books': damaged_books
    }
    return render(request, 'inventory_management/inventory_detail.html', context)

@login_required
@user_passes_test(is_staff)
def adjust_inventory(request, pk):
    inventory_item = get_object_or_404(InventoryItem, pk=pk)
    
    if request.method == 'POST':
        form = InventoryAdjustmentForm(request.POST)
        if form.is_valid():
            adjustment = form.save(commit=False)
            adjustment.inventory_item = inventory_item
            adjustment.performed_by = request.user
            
            # Update inventory counts based on action
            if adjustment.action in ['ADD', 'RETURN']:
                inventory_item.total_copies += adjustment.quantity
                inventory_item.available_copies += adjustment.quantity
            elif adjustment.action in ['REMOVE', 'DAMAGE', 'LOST']:
                inventory_item.total_copies -= adjustment.quantity
                inventory_item.available_copies -= adjustment.quantity
            
            inventory_item.save()
            adjustment.save()
            
            messages.success(request, 'Inventory adjusted successfully.')
            return redirect('inventory:inventory_detail', pk=pk)
    else:
        form = InventoryAdjustmentForm()
    
    return render(request, 'inventory_management/adjust_inventory.html', {
        'form': form,
        'inventory_item': inventory_item
    })

@login_required
@user_passes_test(is_staff)
def report_damaged(request, pk):
    inventory_item = get_object_or_404(InventoryItem, pk=pk)
    
    if request.method == 'POST':
        form = DamagedBookForm(request.POST)
        if form.is_valid():
            damaged_book = form.save(commit=False)
            damaged_book.inventory_item = inventory_item
            damaged_book.save()
            
            # Create inventory log for damaged book
            InventoryLog.objects.create(
                inventory_item=inventory_item,
                action='DAMAGE',
                quantity=1,
                notes=f"Book marked as damaged: {damaged_book.damage_description}",
                performed_by=request.user
            )
            
            inventory_item.available_copies -= 1
            inventory_item.save()
            
            messages.success(request, 'Damaged book reported successfully.')
            return redirect('inventory:inventory_detail', pk=pk)
    else:
        form = DamagedBookForm()
    
    return render(request, 'inventory_management/report_damaged.html', {
        'form': form,
        'inventory_item': inventory_item
    })

@login_required
@user_passes_test(is_staff)
def update_damaged_status(request, damaged_id):
    damaged_book = get_object_or_404(DamagedBook, pk=damaged_id)
    
    if request.method == 'POST':
        form = DamagedBookForm(request.POST, instance=damaged_book)
        if form.is_valid():
            damaged_book = form.save()
            
            # If book is repaired, update inventory
            if damaged_book.status == 'REPAIRED':
                damaged_book.inventory_item.available_copies += 1
                damaged_book.inventory_item.save()
                
                InventoryLog.objects.create(
                    inventory_item=damaged_book.inventory_item,
                    action='RETURN',
                    quantity=1,
                    notes=f"Book repaired and returned to inventory",
                    performed_by=request.user
                )
            
            messages.success(request, 'Damaged book status updated successfully.')
            return redirect('inventory:inventory_detail', pk=damaged_book.inventory_item.pk)
    else:
        form = DamagedBookForm(instance=damaged_book)
    
    return render(request, 'inventory_management/update_damaged_status.html', {
        'form': form,
        'damaged_book': damaged_book
    })

@login_required
@user_passes_test(is_staff)
def inventory_item_create(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            inventory_item = form.save()
            messages.success(request, 'Inventory item created successfully.')
            return redirect('inventory:inventory_detail', pk=inventory_item.pk)
    else:
        form = InventoryItemForm()
    
    return render(request, 'inventory_management/inventory_item_form.html', {
        'form': form,
        'action': 'Create'
    })

@login_required
@user_passes_test(is_staff)
def inventory_item_edit(request, pk):
    inventory_item = get_object_or_404(InventoryItem, pk=pk)
    
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=inventory_item)
        if form.is_valid():
            inventory_item = form.save()
            messages.success(request, 'Inventory item updated successfully.')
            return redirect('inventory:inventory_detail', pk=inventory_item.pk)
    else:
        form = InventoryItemForm(instance=inventory_item)
    
    return render(request, 'inventory_management/inventory_item_form.html', {
        'form': form,
        'inventory_item': inventory_item,
        'action': 'Edit'
    })

@login_required
@user_passes_test(is_staff)
def inventory_item_delete(request, pk):
    inventory_item = get_object_or_404(InventoryItem, pk=pk)
    
    if request.method == 'POST':
        inventory_item.delete()
        messages.success(request, 'Inventory item deleted successfully.')
        return redirect('inventory:inventory_list')
    
    return render(request, 'inventory_management/inventory_item_confirm_delete.html', {
        'inventory_item': inventory_item
    }) 