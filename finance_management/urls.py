from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('dashboard/', views.financial_dashboard, name='dashboard'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/print/', views.print_receipt, name='print_receipt'),
    path('fines/', views.fine_list, name='fine_list'),
    path('fines/collect/', views.fine_collection, name='fine_collection'),
    path('reports/income/', views.income_report, name='income_report'),
    path('reports/expense/', views.expense_report, name='expense_report'),
    path('reports/generate/', views.generate_report, name='generate_report'),
    path('income/', views.IncomeListView.as_view(), name='income_list'),
    path('income/add/', views.IncomeCreateView.as_view(), name='income_create'),
    path('income/<int:pk>/edit/', views.IncomeUpdateView.as_view(), name='income_update'),
    path('income/<int:pk>/delete/', views.IncomeDeleteView.as_view(), name='income_delete'),
    path('expense/', views.ExpenseListView.as_view(), name='expense_list'),
    path('expense/add/', views.ExpenseCreateView.as_view(), name='expense_create'),
    path('expense/<int:pk>/edit/', views.ExpenseUpdateView.as_view(), name='expense_update'),
    path('expense/<int:pk>/delete/', views.ExpenseDeleteView.as_view(), name='expense_delete'),
    path('transaction/create/', views.TransactionCreateView.as_view(), name='transaction_create'),
] 