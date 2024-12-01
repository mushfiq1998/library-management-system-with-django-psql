from django.urls import path
from . import views

app_name = 'circulation'

urlpatterns = [
    path('issue/<int:book_id>/', views.issue_book, name='issue_book'),
    path('return/<int:loan_id>/', views.return_book, name='return_book'),
    path('renew/<int:loan_id>/', views.renew_book, name='renew_book'),
    path('hold/<int:book_id>/', views.place_hold, name='place_hold'),
    path('loans/', views.user_loans, name='user_loans'),
    path('pay-fine/<int:loan_id>/', views.pay_fine, name='pay_fine'),
    path('all-loans/', views.all_loans, name='all_loans'),
    path('overdue/', views.overdue_books, name='overdue_books'),
    path('fines/', views.manage_fines, name='manage_fines'),
    path('loans/list/', views.LoanListView.as_view(), name='loan_list'),
    path('loans/create/', views.LoanCreateView.as_view(), name='loan_create'),
    path('loans/<int:pk>/update/', views.LoanUpdateView.as_view(), name='loan_update'),
    path('loans/<int:pk>/delete/', views.LoanDeleteView.as_view(), name='loan_delete'),
    path('fines/<int:pk>/update/', views.FineUpdateView.as_view(), name='fine_update'),
    path('fines/<int:pk>/', views.fine_detail, name='fine_detail'),
    path('fines/create/', views.FineCreateView.as_view(), name='fine_create'),
    path('holds/', views.BookHoldListView.as_view(), name='bookhold_list'),
    path('holds/create/', views.BookHoldCreateView.as_view(), name='bookhold_create'),
    path('holds/<int:pk>/update/', views.BookHoldUpdateView.as_view(), name='bookhold_update'),
    path('holds/<int:pk>/delete/', views.BookHoldDeleteView.as_view(), name='bookhold_delete'),
] 