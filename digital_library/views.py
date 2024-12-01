from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Q, Avg
from .models import DigitalContent, DigitalLoan, DigitalContentProgress, DigitalContentReview
from .forms import DigitalContentForm, DigitalContentReviewForm, DigitalContentSearchForm
from datetime import timedelta

def is_librarian_or_admin(user):
    return user.role in ['LIBRARIAN', 'ADMIN']

@login_required
def digital_content_list(request):
    form = DigitalContentSearchForm(request.GET)
    content_list = DigitalContent.objects.filter(is_active=True)
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        content_type = form.cleaned_data.get('content_type')
        file_format = form.cleaned_data.get('file_format')
        sort_by = form.cleaned_data.get('sort_by')
        
        if query:
            content_list = content_list.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(isbn__icontains=query)
            )
        
        if content_type:
            content_list = content_list.filter(content_type=content_type)
            
        if file_format:
            content_list = content_list.filter(file_format=file_format)
            
        if sort_by:
            if sort_by == 'rating':
                content_list = content_list.annotate(
                    avg_rating=Avg('reviews__rating')
                ).order_by('-avg_rating')
            else:
                content_list = content_list.order_by(sort_by)
    
    status = request.GET.get('status')
    if status:
        if status == 'in_progress':
            content_list = content_list.filter(
                digitalcontentprogress__user=request.user,
                digitalcontentprogress__completed=False
            )
        elif status == 'completed':
            content_list = content_list.filter(
                digitalcontentprogress__user=request.user,
                digitalcontentprogress__completed=True
            )
        elif status == 'bookmarked':
            content_list = content_list.filter(
                digitalcontentprogress__user=request.user,
                digitalcontentprogress__bookmarks__len__gt=0
            )
    
    return render(request, 'digital_library/content_list.html', {
        'content_list': content_list,
        'form': form
    })

@login_required
def digital_content_detail(request, pk):
    content = get_object_or_404(DigitalContent, pk=pk)
    user_progress = DigitalContentProgress.objects.filter(
        user=request.user,
        content=content
    ).first()
    user_review = DigitalContentReview.objects.filter(
        user=request.user,
        content=content
    ).first()
    
    if request.method == 'POST':
        review_form = DigitalContentReviewForm(request.POST, instance=user_review)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.content = content
            review.save()
            messages.success(request, 'Review submitted successfully.')
            return redirect('digital_library:content_detail', pk=pk)
    else:
        review_form = DigitalContentReviewForm(instance=user_review)
    
    return render(request, 'digital_library/content_detail.html', {
        'content': content,
        'progress': user_progress,
        'review_form': review_form,
        'user_review': user_review,
        'other_reviews': content.reviews.exclude(user=request.user)
    })

@login_required
@user_passes_test(is_librarian_or_admin)
def digital_content_create(request):
    if request.method == 'POST':
        form = DigitalContentForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.save()
            messages.success(request, 'Digital content created successfully.')
            return redirect('digital_library:content_detail', pk=content.pk)
    else:
        form = DigitalContentForm()
    
    return render(request, 'digital_library/content_form.html', {
        'form': form,
        'action': 'Create'
    })

@login_required
@user_passes_test(is_librarian_or_admin)
def digital_content_edit(request, pk):
    content = get_object_or_404(DigitalContent, pk=pk)
    if request.method == 'POST':
        form = DigitalContentForm(request.POST, request.FILES, instance=content)
        if form.is_valid():
            form.save()
            messages.success(request, 'Digital content updated successfully.')
            return redirect('digital_library:content_detail', pk=pk)
    else:
        form = DigitalContentForm(instance=content)
    
    return render(request, 'digital_library/content_form.html', {
        'form': form,
        'content': content,
        'action': 'Edit'
    })

@login_required
@user_passes_test(is_librarian_or_admin)
def digital_content_delete(request, pk):
    content = get_object_or_404(DigitalContent, pk=pk)
    if request.method == 'POST':
        content.is_active = False
        content.save()
        messages.success(request, 'Digital content deleted successfully.')
        return redirect('digital_library:content_list')
    return render(request, 'digital_library/content_confirm_delete.html', {
        'content': content
    })

@login_required
def borrow_digital_content(request, pk):
    content = get_object_or_404(DigitalContent, pk=pk)
    
    # Check if user already has an active loan
    existing_loan = DigitalLoan.objects.filter(
        user=request.user,
        content=content,
        status='ACTIVE'
    ).exists()
    
    if existing_loan:
        messages.error(request, 'You already have an active loan for this content.')
    else:
        loan = DigitalLoan.objects.create(
            user=request.user,
            content=content,
            due_date=timezone.now() + timedelta(days=14)  # 2-week loan period
        )
        messages.success(request, 'Content borrowed successfully.')
    
    return redirect('digital_library:content_detail', pk=pk)

@login_required
def return_digital_content(request, pk):
    loan = get_object_or_404(
        DigitalLoan,
        content_id=pk,
        user=request.user,
        status='ACTIVE'
    )
    loan.status = 'RETURNED'
    loan.return_date = timezone.now()
    loan.save()
    messages.success(request, 'Content returned successfully.')
    return redirect('digital_library:my_loans')

@login_required
def my_digital_loans(request):
    active_loans = DigitalLoan.objects.filter(
        user=request.user,
        status='ACTIVE'
    ).order_by('-loan_date')
    past_loans = DigitalLoan.objects.filter(
        user=request.user,
        status__in=['RETURNED', 'EXPIRED']
    ).order_by('-return_date')
    
    return render(request, 'digital_library/my_loans.html', {
        'active_loans': active_loans,
        'past_loans': past_loans
    })

@login_required
def read_digital_content(request, pk):
    content = get_object_or_404(DigitalContent, pk=pk)
    progress, created = DigitalContentProgress.objects.get_or_create(
        user=request.user,
        content=content
    )
    return render(request, 'digital_library/reader.html', {
        'content': content,
        'progress': progress
    })

@login_required
def listen_digital_content(request, pk):
    content = get_object_or_404(DigitalContent, pk=pk)
    progress, created = DigitalContentProgress.objects.get_or_create(
        user=request.user,
        content=content
    )
    return render(request, 'digital_library/audio_player.html', {
        'content': content,
        'progress': progress
    })

@login_required
def update_progress(request, pk):
    if request.method == 'POST':
        content = get_object_or_404(DigitalContent, pk=pk)
        progress = DigitalContentProgress.objects.get_or_create(
            user=request.user,
            content=content
        )[0]
        
        if content.content_type == 'EBOOK':
            progress.current_page = request.POST.get('current_page', 0)
        else:
            progress.current_position = request.POST.get('current_position', 0)
        
        progress.completed = request.POST.get('completed', False)
        progress.save()
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def add_bookmark(request, pk):
    if request.method == 'POST':
        content = get_object_or_404(DigitalContent, pk=pk)
        progress = DigitalContentProgress.objects.get_or_create(
            user=request.user,
            content=content
        )[0]
        
        bookmark_data = {
            'position': request.POST.get('position'),
            'title': request.POST.get('title'),
            'note': request.POST.get('note', '')
        }
        
        if not progress.bookmarks:
            progress.bookmarks = []
        progress.bookmarks.append(bookmark_data)
        progress.save()
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def add_note(request, pk):
    if request.method == 'POST':
        content = get_object_or_404(DigitalContent, pk=pk)
        progress = DigitalContentProgress.objects.get_or_create(
            user=request.user,
            content=content
        )[0]
        
        position = request.POST.get('position')
        note_text = request.POST.get('note')
        
        if not progress.notes:
            progress.notes = {}
        progress.notes[position] = note_text
        progress.save()
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def download_digital_content(request, pk):
    content = get_object_or_404(DigitalContent, pk=pk)
    
    # Check if user has an active loan
    loan = DigitalLoan.objects.filter(
        content=content,
        user=request.user,
        status='ACTIVE'
    ).first()
    
    if not loan:
        # If no active loan, create one
        loan = DigitalLoan.objects.create(
            user=request.user,
            content=content,
            due_date=timezone.now() + timedelta(days=14),  # 2-week loan period
            status='ACTIVE'
        )
        messages.info(request, 'A new loan has been created for this content.')
    
    # Update loan statistics
    loan.download_count += 1
    loan.last_accessed = timezone.now()
    loan.save()
    
    # Determine content type based on file format
    content_types = {
        'PDF': 'application/pdf',
        'EPUB': 'application/epub+zip',
        'MOBI': 'application/x-mobipocket-ebook',
        'MP3': 'audio/mpeg',
        'M4B': 'audio/mp4'
    }
    
    content_type = content_types.get(content.file_format, 'application/octet-stream')
    
    try:
        response = HttpResponse(content.file, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{content.file.name}"'
        return response
    except Exception as e:
        messages.error(request, f'Error downloading file: {str(e)}')
        return redirect('digital_library:content_detail', pk=pk)

@login_required
def review_digital_content(request, pk):
    content = get_object_or_404(DigitalContent, pk=pk)
    
    # Check if user has already reviewed this content
    existing_review = DigitalContentReview.objects.filter(
        user=request.user,
        content=content
    ).first()
    
    if request.method == 'POST':
        form = DigitalContentReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.content = content
            review.save()
            messages.success(request, 'Review submitted successfully.')
            return redirect('digital_library:content_detail', pk=pk)
    else:
        form = DigitalContentReviewForm(instance=existing_review)
    
    return render(request, 'digital_library/review_form.html', {
        'form': form,
        'content': content,
        'existing_review': existing_review,
        'action': 'Edit' if existing_review else 'Create'
    }) 