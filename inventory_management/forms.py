from django import forms
from .models import InventoryItem, InventoryLog, DamagedBook
from book_catalog.models import Book

class InventoryItemForm(forms.ModelForm):
    book = forms.ModelChoiceField(
        queryset=Book.objects.all(),
        empty_label="Select a Book",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = InventoryItem
        fields = ['book', 'total_copies', 'available_copies', 'minimum_threshold']
        widgets = {
            'total_copies': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'available_copies': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'minimum_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            })
        }
        
    def clean(self):
        cleaned_data = super().clean()
        total_copies = cleaned_data.get('total_copies')
        available_copies = cleaned_data.get('available_copies')
        
        if available_copies > total_copies:
            raise forms.ValidationError(
                "Available copies cannot exceed total copies"
            )
        
        # Check if an inventory item already exists for this book
        book = cleaned_data.get('book')
        if book and InventoryItem.objects.filter(book=book).exists():
            raise forms.ValidationError(
                "An inventory item already exists for this book"
            )
            
        return cleaned_data

class InventoryAdjustmentForm(forms.ModelForm):
    class Meta:
        model = InventoryLog
        fields = ['action', 'quantity', 'notes']
        widgets = {
            'action': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }

class DamagedBookForm(forms.ModelForm):
    class Meta:
        model = DamagedBook
        fields = ['damage_description', 'status', 'repair_cost', 'repair_notes']
        widgets = {
            'damage_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'repair_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'repair_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        } 