from django import forms
from .models import BookLoan, BookHold
from book_catalog.models import Book
from user_management.models import User

class BookLoanForm(forms.ModelForm):
    book = forms.ModelChoiceField(
        queryset=Book.objects.filter(availability_status='AVAILABLE'),
        empty_label="Select a Book",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        empty_label="Select a User",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = BookLoan
        fields = ['book', 'user']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update book queryset to show only available books
        self.fields['book'].queryset = Book.objects.filter(availability_status='AVAILABLE') 

class FineManagementForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        empty_label="Select a User",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    book = forms.ModelChoiceField(
        queryset=Book.objects.all(),
        empty_label="Select a Book",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = BookLoan
        fields = ['user', 'book', 'fine_amount', 'fine_paid']
        widgets = {
            'fine_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'fine_paid': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def clean_fine_amount(self):
        amount = self.cleaned_data['fine_amount']
        if amount < 0:
            raise forms.ValidationError("Fine amount cannot be negative")
        return amount

class BookHoldForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        empty_label="Select a User",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    book = forms.ModelChoiceField(
        queryset=Book.objects.all(),
        empty_label="Select a Book",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = BookHold
        fields = ['user', 'book', 'status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'})
        }