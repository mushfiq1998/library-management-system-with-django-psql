from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegistrationForm, UserProfileUpdateForm, AdminUserEditForm
from .models import User, UserProfile
from membership_management.models import RenewalReminder, Membership
from django.utils import timezone

def is_admin_or_librarian(user):
    return user.role in ['ADMIN', 'LIBRARIAN']

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create UserProfile
            UserProfile.objects.create(
                user=user,
                library_card_number=f"LIB{user.id:06d}"
            )
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to the Library System.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'user_management/register.html', {'form': form})

@login_required
def dashboard(request):
    context = {}
    
    # Get user's membership if it exists
    try:
        user_membership = Membership.objects.filter(user=request.user, is_active=True).first()
        context['user_membership'] = user_membership
    except Membership.DoesNotExist:
        context['user_membership'] = None
    
    if request.user.role == 'ADMIN':
        # Add pending reminders count for admin users
        pending_reminders_count = RenewalReminder.objects.filter(
            sent=False,
            reminder_date__lte=timezone.now()
        ).count()
        context['pending_reminders_count'] = pending_reminders_count
    
    return render(request, 'user_management/dashboard.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            # Update the fields
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileUpdateForm(instance=request.user)
    
    context = {
        'form': form,
        'user_profile': request.user.profile,
    }
    return render(request, 'user_management/profile.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Keep the user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'user_management/change_password.html', {'form': form})

@login_required
@user_passes_test(is_admin_or_librarian)
def manage_users(request):
    users = User.objects.all().select_related('profile')
    context = {
        'users': users,
    }
    return render(request, 'user_management/manage_users.html', context)

@login_required
@user_passes_test(is_admin_or_librarian)
def edit_user(request, user_id):
    user_to_edit = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user_to_edit.username} has been updated successfully.')
            return redirect('manage_users')
    else:
        form = AdminUserEditForm(instance=user_to_edit)
    
    return render(request, 'user_management/edit_user.html', {
        'form': form,
        'edited_user': user_to_edit
    })

@login_required
@user_passes_test(is_admin_or_librarian)
def delete_user(request, user_id):
    user_to_delete = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        username = user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f'User {username} has been deleted successfully.')
        return redirect('manage_users')
    
    return render(request, 'user_management/delete_user.html', {
        'user_to_delete': user_to_delete
    })
