from django import forms
from .models import Income, Expense, Transaction, Fine, Payment

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'type',
            'category',
            'amount',
            'payment_method',
            'description',
            'reference_number'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero")
        return amount

class FineForm(forms.ModelForm):
    class Meta:
        model = Fine
        fields = [
            'user',
            'amount',
            'reason',
            'due_date'
        ]
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Fine amount must be greater than zero")
        return amount

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'payer',
            'transaction'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show income transactions that don't already have a payment
        self.fields['transaction'].queryset = Transaction.objects.filter(
            type='INCOME',
            payment__isnull=True
        )

class ReportGenerationForm(forms.Form):
    REPORT_TYPES = [
        ('all', 'All Transactions'),
        ('income', 'Income Only'),
        ('expense', 'Expenses Only'),
    ]

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    report_type = forms.ChoiceField(
        choices=REPORT_TYPES,
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date cannot be after end date")
        
        return cleaned_data

class FineCollectionForm(forms.Form):
    fine = forms.ModelChoiceField(
        queryset=Fine.objects.filter(paid=False),
        empty_label="Select a fine to collect",
        required=True
    )
    payment_method = forms.ChoiceField(
        choices=Transaction.PAYMENT_METHODS,
        required=True
    )
    collected_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )

    def clean_collected_amount(self):
        amount = self.cleaned_data.get('collected_amount')
        fine = self.cleaned_data.get('fine')
        
        if fine and amount > fine.amount:
            raise forms.ValidationError("Collected amount cannot exceed fine amount")
        
        return amount

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = [
            'category',
            'amount',
            'payment_method',
            'description',
            'received_from',
            'reference_number'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero")
        return amount

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            'category',
            'amount',
            'payment_method',
            'description',
            'paid_to',
            'invoice_number'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero")
        return amount 