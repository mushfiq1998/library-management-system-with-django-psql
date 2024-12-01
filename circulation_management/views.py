from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import BookLoan, BookHold, CirculationRule
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test
from .forms import BookLoanForm
from datetime import timedelta
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import UpdateView
from .forms import FineManagementForm
from django.db.models import Sum
from .forms import BookHoldForm

@login_required
def issue_book(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404('books.Book', id=book_id)
        rule = CirculationRule.objects.first()
        
        # Check if user has reached maximum books limit
        active_loans = BookLoan.objects.filter(
            user=request.user,
            status__in=['issued', 'overdue']
        ).count()
        
        if active_loans >= rule.max_books_per_user:
            messages.error(request, 'You have reached the maximum number of books allowed.')
            return redirect('book_detail', book_id=book_id)

        # Create new loan
        loan = BookLoan.objects.create(
            user=request.user,
            book=book,
        )
        messages.success(request, f'Successfully issued: {book.title}')
        return redirect('user_loans')

@login_required
def return_book(request, loan_id):
    loan = get_object_or_404(BookLoan, id=loan_id, user=request.user)
    if request.method == 'POST':
        loan.return_date = timezone.now()
        loan.status = 'returned'
        loan.calculate_fine()
        loan.save()
        
        # Check for holds and notify next user
        next_hold = BookHold.objects.filter(
            book=loan.book,
            status='active'
        ).first()
        
        if next_hold:
            next_hold.notification_sent = True
            next_hold.save()
            messages.info(request, 'Book returned successfully. Fine amount: ${}'.format(loan.fine_amount))
        
        return redirect('circulation:user_loans')

@login_required
def renew_book(request, loan_id):
    loan = get_object_or_404(BookLoan, id=loan_id, user=request.user)
    rule = CirculationRule.objects.first()
    
    if request.method == 'POST':
        if loan.renewals >= rule.max_renewals:
            messages.error(request, 'Maximum renewals reached for this book.')
        elif BookHold.objects.filter(book=loan.book, status='active').exists():
            messages.error(request, 'Cannot renew - book has active hold requests.')
        else:
            loan.due_date = loan.due_date + timedelta(days=rule.loan_period_days)
            loan.renewals += 1
            loan.save()
            messages.success(request, 'Book renewed successfully.')
        
        return redirect('circulation:user_loans')

@login_required
def place_hold(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404('books.Book', id=book_id)
        
        # Check if user already has a hold on this book
        existing_hold = BookHold.objects.filter(
            user=request.user,
            book=book,
            status='active'
        ).exists()
        
        if existing_hold:
            messages.error(request, 'You already have a hold on this book.')
        else:
            BookHold.objects.create(
                user=request.user,
                book=book
            )
            messages.success(request, 'Hold placed successfully.')
        
        return redirect('book_detail', book_id=book_id)

@login_required
def user_loans(request):
    loans = BookLoan.objects.filter(user=request.user).order_by('-issue_date')
    holds = BookHold.objects.filter(user=request.user, status='active')
    
    return render(request, 'circulation_management/user_loans.html', {
        'loans': loans,
        'holds': holds
    })

@login_required
def pay_fine(request, loan_id):
    loan = get_object_or_404(BookLoan, id=loan_id, user=request.user)
    
    if request.method == 'POST':
        loan.fine_paid = True
        loan.save()
        messages.success(request, f'Fine payment of ${loan.fine_amount} processed successfully.')
        return redirect('circulation:user_loans')

@login_required
@user_passes_test(lambda u: u.role in ['LIBRARIAN', 'ADMIN'])
def all_loans(request):
    loans = BookLoan.objects.all().order_by('-issue_date')
    return render(request, 'circulation_management/all_loans.html', {
        'loans': loans
    })

@login_required
@user_passes_test(lambda u: u.role in ['LIBRARIAN', 'ADMIN'])
def overdue_books(request):
    overdue_loans = BookLoan.objects.filter(
        status='issued',
        due_date__lt=timezone.now()
    ).order_by('due_date')
    return render(request, 'circulation_management/overdue_books.html', {
        'overdue_loans': overdue_loans
    })

@login_required
@user_passes_test(lambda u: u.role in ['LIBRARIAN', 'ADMIN'])
def manage_fines(request):
    # Filter options
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    unpaid_fines = BookLoan.objects.filter(fine_amount__gt=0)
    
    if status == 'paid':
        unpaid_fines = unpaid_fines.filter(fine_paid=True)
    elif status == 'unpaid':
        unpaid_fines = unpaid_fines.filter(fine_paid=False)
    
    if search:
        unpaid_fines = unpaid_fines.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(book__title__icontains=search)
        )
    
    unpaid_fines = unpaid_fines.order_by('-fine_amount')
    
    context = {
        'unpaid_fines': unpaid_fines,
        'status': status,
        'search': search,
        'total_unpaid': unpaid_fines.filter(fine_paid=False).aggregate(Sum('fine_amount'))['fine_amount__sum'] or 0,
    }
    return render(request, 'circulation_management/manage_fines.html', context)

@login_required
@user_passes_test(lambda u: u.role in ['LIBRARIAN', 'ADMIN'])
def fine_detail(request, pk):
    loan = get_object_or_404(BookLoan, pk=pk)
    return render(request, 'circulation_management/fine_detail.html', {'loan': loan})

class LibrarianRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in ['LIBRARIAN', 'ADMIN']

class LoanListView(LoginRequiredMixin, LibrarianRequiredMixin, ListView):
    model = BookLoan
    template_name = 'circulation_management/loan_list.html'
    context_object_name = 'loans'
    ordering = ['-issue_date']

class LoanCreateView(LoginRequiredMixin, LibrarianRequiredMixin, CreateView):
    model = BookLoan
    form_class = BookLoanForm
    template_name = 'circulation_management/loan_form.html'
    success_url = reverse_lazy('circulation:loan_list')

    def form_valid(self, form):
        loan = form.save(commit=False)
        # Set the due date based on circulation rules
        rule = CirculationRule.objects.first()
        if not rule:
            # Create a default rule if none exists
            rule = CirculationRule.objects.create(
                loan_period_days=14,
                max_renewals=2,
                fine_per_day=1.00,
                max_books_per_user=5
            )
        
        loan.due_date = timezone.now() + timedelta(days=rule.loan_period_days)
        loan.save()
        
        # Update book availability
        book = loan.book
        book.availability_status = 'ISSUED'
        book.save()
        
        messages.success(self.request, f'Book "{book.title}" has been issued to {loan.user.get_full_name()}')
        return super().form_valid(form)

class LoanUpdateView(LoginRequiredMixin, LibrarianRequiredMixin, UpdateView):
    model = BookLoan
    form_class = BookLoanForm
    template_name = 'circulation_management/loan_form.html'
    success_url = reverse_lazy('circulation:loan_list')

class LoanDeleteView(LoginRequiredMixin, LibrarianRequiredMixin, DeleteView):
    model = BookLoan
    template_name = 'circulation_management/loan_confirm_delete.html'
    success_url = reverse_lazy('circulation:loan_list')

class FineUpdateView(LoginRequiredMixin, LibrarianRequiredMixin, UpdateView):
    model = BookLoan
    form_class = FineManagementForm
    template_name = 'circulation_management/fine_form.html'
    success_url = reverse_lazy('circulation:manage_fines')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Fine updated successfully.')
        return response

class FineCreateView(LoginRequiredMixin, LibrarianRequiredMixin, CreateView):
    model = BookLoan
    form_class = FineManagementForm
    template_name = 'circulation_management/fine_form.html'
    success_url = reverse_lazy('circulation:manage_fines')

    def form_valid(self, form):
        loan = form.save(commit=False)
        loan.issue_date = timezone.now()
        loan.due_date = timezone.now()
        loan.return_date = timezone.now()
        loan.status = 'returned'
        loan.save()
        messages.success(self.request, 'Fine created successfully.')
        return super().form_valid(form)

class BookHoldListView(LoginRequiredMixin, LibrarianRequiredMixin, ListView):
    model = BookHold
    template_name = 'circulation_management/bookhold_list.html'
    context_object_name = 'holds'
    ordering = ['-request_date']

class BookHoldCreateView(LoginRequiredMixin, LibrarianRequiredMixin, CreateView):
    model = BookHold
    form_class = BookHoldForm
    template_name = 'circulation_management/bookhold_form.html'
    success_url = reverse_lazy('circulation:bookhold_list')

class BookHoldUpdateView(LoginRequiredMixin, LibrarianRequiredMixin, UpdateView):
    model = BookHold
    form_class = BookHoldForm
    template_name = 'circulation_management/bookhold_form.html'
    success_url = reverse_lazy('circulation:bookhold_list')

class BookHoldDeleteView(LoginRequiredMixin, LibrarianRequiredMixin, DeleteView):
    model = BookHold
    template_name = 'circulation_management/bookhold_confirm_delete.html'
    success_url = reverse_lazy('circulation:bookhold_list')
  