from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Membership, MembershipPlan, MemberActivity, RenewalReminder
from .forms import MembershipForm, MembershipPlanForm, MemberActivityForm, RenewalReminderForm

def is_admin(user):
    return user.role == 'ADMIN'

@login_required
@user_passes_test(is_admin)
def membership_list(request):
    memberships = Membership.objects.all()
    return render(request, 'membership_management/membership_list.html', {'memberships': memberships})

@login_required
@user_passes_test(is_admin)
def membership_create(request):
    if request.method == 'POST':
        form = MembershipForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Membership created successfully.')
            return redirect('membership_list')
    else:
        form = MembershipForm()
    return render(request, 'membership_management/membership_form.html', {'form': form, 'action': 'Create'})

@login_required
@user_passes_test(is_admin)
def membership_edit(request, pk):
    membership = get_object_or_404(Membership, pk=pk)
    if request.method == 'POST':
        form = MembershipForm(request.POST, instance=membership)
        if form.is_valid():
            form.save()
            messages.success(request, 'Membership updated successfully.')
            return redirect('membership_list')
    else:
        form = MembershipForm(instance=membership)
    return render(request, 'membership_management/membership_form.html', {'form': form, 'action': 'Edit'})

@login_required
@user_passes_test(is_admin)
def membership_plan_list(request):
    plans = MembershipPlan.objects.all()
    context = {'plans': plans}
    return render(
        request, 'membership_management/membership_plan_list.html', context)

@login_required
@user_passes_test(is_admin)
def membership_plan_create(request):
    if request.method == 'POST':
        form = MembershipPlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Membership plan created successfully.')
            return redirect('membership:membership_plan_list')
    else:
        form = MembershipPlanForm()
    return render(request, 'membership_management/membership_plan_form.html', {
        'form': form,
        'action': 'Create'
    })

@login_required
@user_passes_test(is_admin)
def membership_plan_edit(request, pk):
    plan = get_object_or_404(MembershipPlan, pk=pk)
    if request.method == 'POST':
        form = MembershipPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Membership plan updated successfully.')
            return redirect('membership:membership_plan_list')
    else:
        form = MembershipPlanForm(instance=plan)
    return render(request, 'membership_management/membership_plan_form.html', {
        'form': form,
        'action': 'Edit'
    })

@login_required
@user_passes_test(is_admin)
def membership_plan_delete(request, pk):
    plan = get_object_or_404(MembershipPlan, pk=pk)
    if request.method == 'POST':
        plan.delete()
        messages.success(request, 'Membership plan deleted successfully.')
        return redirect('membership:membership_plan_list')
    return redirect('membership:membership_plan_list')

@login_required
def member_activities(request, membership_id):
    membership = get_object_or_404(Membership, id=membership_id)
    activities = membership.activities.all()
    return render(request, 'membership_management/member_activities.html', {
        'membership': membership,
        'activities': activities
    })

@login_required
@user_passes_test(is_admin)
def renewal_reminders(request):
    reminders = RenewalReminder.objects.filter(sent=False).order_by('reminder_date')
    return render(request, 'membership_management/renewal_reminders.html', {
        'reminders': reminders
    })

@login_required
@user_passes_test(is_admin)
def update_reminder_response(request, reminder_id):
    if request.method == 'POST':
        reminder = get_object_or_404(RenewalReminder, id=reminder_id)
        response = request.POST.get('response')
        reminder.update_response(response)
        
        if response == 'RENEWED':
            # Create new activity
            reminder.membership.record_activity(
                'RENEW',
                'Membership renewed after reminder'
            )
            
        messages.success(request, 'Reminder response updated successfully.')
        return redirect('membership:renewal_reminders')

@login_required
@user_passes_test(is_admin)
def activity_list(request):
    activities = MemberActivity.objects.all().order_by('-activity_date')
    return render(request, 'membership_management/activity_list.html', {
        'activities': activities
    })

@login_required
@user_passes_test(is_admin)
def activity_create(request):
    if request.method == 'POST':
        form = MemberActivityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Activity recorded successfully.')
            return redirect('membership:activity_list')
    else:
        form = MemberActivityForm()
    return render(request, 'membership_management/activity_form.html', {
        'form': form,
        'action': 'Create'
    })

@login_required
@user_passes_test(is_admin)
def activity_edit(request, pk):
    activity = get_object_or_404(MemberActivity, pk=pk)
    if request.method == 'POST':
        form = MemberActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            messages.success(request, 'Activity updated successfully.')
            return redirect('membership:activity_list')
    else:
        form = MemberActivityForm(instance=activity)
    return render(request, 'membership_management/activity_form.html', {
        'form': form,
        'activity': activity,
        'action': 'Edit'
    })

@login_required
@user_passes_test(is_admin)
def activity_delete(request, pk):
    activity = get_object_or_404(MemberActivity, pk=pk)
    if request.method == 'POST':
        activity.delete()
        messages.success(request, 'Activity deleted successfully.')
    return redirect('membership:activity_list')

@login_required
@user_passes_test(is_admin)
def reminder_create(request):
    if request.method == 'POST':
        form = RenewalReminderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reminder created successfully.')
            return redirect('membership:renewal_reminders')
    else:
        form = RenewalReminderForm()
    return render(request, 'membership_management/reminder_form.html', {
        'form': form,
        'action': 'Create'
    })

@login_required
@user_passes_test(is_admin)
def reminder_edit(request, pk):
    reminder = get_object_or_404(RenewalReminder, pk=pk)
    if request.method == 'POST':
        form = RenewalReminderForm(request.POST, instance=reminder)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reminder updated successfully.')
            return redirect('membership:renewal_reminders')
    else:
        form = RenewalReminderForm(instance=reminder)
    return render(request, 'membership_management/reminder_form.html', {
        'form': form,
        'reminder': reminder,
        'action': 'Edit'
    })

@login_required
@user_passes_test(is_admin)
def reminder_delete(request, pk):
    reminder = get_object_or_404(RenewalReminder, pk=pk)
    if request.method == 'POST':
        reminder.delete()
        messages.success(request, 'Reminder deleted successfully.')
    return redirect('membership:renewal_reminders') 