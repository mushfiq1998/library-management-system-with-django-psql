from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from .models import Transaction, Fine, Payment, Income, Expense
from .forms import (
    TransactionForm, 
    FineForm, 
    PaymentForm, 
    ReportGenerationForm,
    FineCollectionForm,
    IncomeForm,
    ExpenseForm
)
from datetime import datetime, timedelta
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

def is_finance_staff(user):
    return user.role in ['ADMIN', 'LIBRARIAN']

@login_required
@user_passes_test(is_finance_staff)
def financial_dashboard(request):
    # Get current month's data
    today = timezone.now()
    month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Calculate total income and expenses
    total_income = Transaction.objects.filter(
        type='INCOME',
        date__gte=month_start
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    total_expenses = Transaction.objects.filter(
        type='EXPENSE',
        date__gte=month_start
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Get pending fines
    pending_fines = Fine.objects.filter(paid=False).count()
    
    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_amount': total_income - total_expenses,
        'pending_fines': pending_fines,
        'recent_transactions': Transaction.objects.all().order_by('-date')[:5],
    }
    return render(request, 'finance_management/dashboard.html', context)

@login_required
@user_passes_test(is_finance_staff)
def transaction_list(request):
    transactions = Transaction.objects.all().order_by('-date')
    return render(request, 'finance_management/transaction_list.html', {'transactions': transactions})

@login_required
@user_passes_test(is_finance_staff)
def fine_list(request):
    fines = Fine.objects.all().order_by('-date_issued')
    return render(request, 'finance_management/fine_list.html', {'fines': fines})

@login_required
@user_passes_test(is_finance_staff)
def payment_list(request):
    payments = Payment.objects.all().order_by('-payment_date')
    return render(request, 'finance_management/payment_list.html', {'payments': payments})

@login_required
@user_passes_test(is_finance_staff)
def fine_collection(request):
    if request.method == 'POST':
        form = FineCollectionForm(request.POST)
        if form.is_valid():
            fine = form.cleaned_data['fine']
            payment_method = form.cleaned_data['payment_method']
            collected_amount = form.cleaned_data['collected_amount']
            
            # Create transaction for the fine payment
            transaction = Transaction.objects.create(
                type='INCOME',
                category='FINE',
                amount=collected_amount,
                payment_method=payment_method,
                description=f"Fine payment for {fine.user.username} - {fine.reason}",
                recorded_by=request.user
            )
            
            # Create payment record
            payment = Payment.objects.create(
                transaction=transaction,
                payer=fine.user
            )
            
            # Update fine status
            fine.paid = True
            fine.payment_date = timezone.now()
            fine.transaction = transaction
            fine.save()
            
            messages.success(request, f"Successfully collected fine payment of {collected_amount}")
            return redirect('finance:fine_list')
    else:
        form = FineCollectionForm()
        # Add fine details to the select options
        for choice in form.fields['fine'].choices:
            if choice[0]:  # Skip the empty choice
                fine = Fine.objects.get(pk=choice[0])
                choice[1].attrs['data-fine'] = json.dumps({
                    'user': fine.user.username,
                    'amount': str(fine.amount),
                    'reason': fine.reason,
                    'due_date': fine.due_date.strftime('%Y-%m-%d %H:%M')
                }, cls=DjangoJSONEncoder)
    
    return render(request, 'finance_management/fine_collection.html', {'form': form})

@login_required
@user_passes_test(is_finance_staff)
def income_report(request):
    transactions = Transaction.objects.filter(type='INCOME').order_by('-date')
    total = transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'transactions': transactions,
        'total': total,
        'report_type': 'Income'
    }
    return render(request, 'finance_management/report.html', context)

@login_required
@user_passes_test(is_finance_staff)
def expense_report(request):
    transactions = Transaction.objects.filter(type='EXPENSE').order_by('-date')
    total = transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'transactions': transactions,
        'total': total,
        'report_type': 'Expense'
    }
    return render(request, 'finance_management/report.html', context)

@login_required
@user_passes_test(is_finance_staff)
def generate_report(request):
    if request.method == 'POST':
        form = ReportGenerationForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            report_type = form.cleaned_data['report_type']
            
            # Generate report based on parameters
            transactions = Transaction.objects.filter(
                date__date__range=[start_date, end_date]
            )
            
            if report_type == 'income':
                transactions = transactions.filter(type='INCOME')
            elif report_type == 'expense':
                transactions = transactions.filter(type='EXPENSE')
            
            total = transactions.aggregate(Sum('amount'))['amount__sum'] or 0
            
            context = {
                'transactions': transactions,
                'start_date': start_date,
                'end_date': end_date,
                'report_type': report_type,
                'total': total,
                'form': form
            }
            return render(request, 'finance_management/report_result.html', context)
    else:
        form = ReportGenerationForm()
    
    return render(request, 'finance_management/generate_report.html', {'form': form})

@login_required
@user_passes_test(is_finance_staff)
def print_receipt(request):
    receipt_number = request.GET.get('receipt')
    payment = get_object_or_404(Payment, receipt_number=receipt_number)
    
    context = {
        'payment': payment,
        'library_name': 'Your Library Name',  # Customize this
        'library_address': 'Your Library Address',  # Customize this
        'library_contact': 'Contact Information',  # Customize this
    }
    
    return render(request, 'finance_management/receipt_print.html', context)

# Income Views
class IncomeListView(ListView):
    model = Income
    template_name = 'finance_management/income_list.html'
    context_object_name = 'incomes'
    ordering = ['-date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calculate total income
        total_amount = Income.objects.aggregate(total=Sum('amount'))['total'] or 0
        context['total_amount'] = total_amount
        return context

class IncomeCreateView(CreateView):
    model = Income
    form_class = IncomeForm
    template_name = 'finance_management/income_form.html'
    success_url = reverse_lazy('finance:income_list')

    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        return super().form_valid(form)

class IncomeUpdateView(UpdateView):
    model = Income
    form_class = IncomeForm
    template_name = 'finance_management/income_form.html'
    success_url = reverse_lazy('finance:income_list')

class IncomeDeleteView(DeleteView):
    model = Income
    template_name = 'finance_management/income_confirm_delete.html'
    success_url = reverse_lazy('finance:income_list')

# Expense Views
class ExpenseListView(ListView):
    model = Expense
    template_name = 'finance_management/expense_list.html'
    context_object_name = 'expenses'
    ordering = ['-date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calculate total expenses
        total_amount = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
        context['total_amount'] = total_amount
        return context

class ExpenseCreateView(CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'finance_management/expense_form.html'
    success_url = reverse_lazy('finance:expense_list')

    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        return super().form_valid(form)

class ExpenseUpdateView(UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'finance_management/expense_form.html'
    success_url = reverse_lazy('finance:expense_list')

class ExpenseDeleteView(DeleteView):
    model = Expense
    template_name = 'finance_management/expense_confirm_delete.html'
    success_url = reverse_lazy('finance:expense_list')

class TransactionCreateView(CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'finance_management/transaction_form.html'
    success_url = reverse_lazy('finance:transaction_list')

    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        return super().form_valid(form) 