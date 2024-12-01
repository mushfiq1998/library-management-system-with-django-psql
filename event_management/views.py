from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Avg
from .models import Event, EventRegistration, EventFeedback, EventResource
from .forms import (
    EventForm, EventRegistrationForm, EventFeedbackForm,
    EventResourceForm, EventSearchForm
)

def is_staff(user):
    return user.role in ['ADMIN', 'LIBRARIAN']

@login_required
def event_list(request):
    form = EventSearchForm(request.GET)
    events = Event.objects.filter(is_public=True)
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        event_type = form.cleaned_data.get('event_type')
        status = form.cleaned_data.get('status')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        sort_by = form.cleaned_data.get('sort_by')
        
        if query:
            events = events.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
        
        if event_type:
            events = events.filter(event_type=event_type)
            
        if status:
            events = events.filter(status=status)
            
        if date_from:
            events = events.filter(start_date__gte=date_from)
            
        if date_to:
            events = events.filter(end_date__lte=date_to)
            
        if sort_by:
            events = events.order_by(sort_by)
    
    return render(request, 'event_management/event_list.html', {
        'events': events,
        'form': form
    })

@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    user_registration = EventRegistration.objects.filter(
        event=event,
        user=request.user
    ).first()
    user_feedback = EventFeedback.objects.filter(
        event=event,
        user=request.user
    ).first()
    
    context = {
        'event': event,
        'registration': user_registration,
        'feedback': user_feedback,
        'can_register': not event.is_full and not event.registration_closed,
        'resources': event.resources.filter(is_public=True)
    }
    return render(request, 'event_management/event_detail.html', context)

@login_required
@user_passes_test(is_staff)
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Event created successfully.')
            return redirect('event:event_detail', pk=event.pk)
    else:
        form = EventForm()
    
    return render(request, 'event_management/event_form.html', {
        'form': form,
        'action': 'Create'
    })

@login_required
@user_passes_test(is_staff)
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully.')
            return redirect('event:event_detail', pk=pk)
    else:
        form = EventForm(instance=event)
    
    return render(request, 'event_management/event_form.html', {
        'form': form,
        'event': event,
        'action': 'Edit'
    })

@login_required
@user_passes_test(is_staff)
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully.')
        return redirect('event:event_list')
    return render(request, 'event_management/event_confirm_delete.html', {
        'event': event
    })

@login_required
def event_register(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    if event.is_full:
        messages.error(request, 'Sorry, this event is full.')
        return redirect('event:event_detail', pk=pk)
    
    if event.registration_closed:
        messages.error(request, 'Registration is closed for this event.')
        return redirect('event:event_detail', pk=pk)
    
    if request.method == 'POST':
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.event = event
            registration.user = request.user
            registration.save()
            messages.success(request, 'Registration successful.')
            return redirect('event:event_detail', pk=pk)
    else:
        form = EventRegistrationForm()
    
    return render(request, 'event_management/registration_form.html', {
        'form': form,
        'event': event
    })

@login_required
def registration_cancel(request, pk):
    registration = get_object_or_404(
        EventRegistration,
        pk=pk,
        user=request.user
    )
    
    if request.method == 'POST':
        registration.status = 'CANCELLED'
        registration.save()
        messages.success(request, 'Registration cancelled successfully.')
        return redirect('event:my_registrations')
    
    return render(request, 'event_management/registration_cancel.html', {
        'registration': registration
    })

@login_required
def my_registrations(request):
    registrations = EventRegistration.objects.filter(
        user=request.user
    ).order_by('-registration_date')
    
    return render(request, 'event_management/my_registrations.html', {
        'registrations': registrations
    })

@login_required
def submit_feedback(request, pk):
    event = get_object_or_404(Event, pk=pk)
    existing_feedback = EventFeedback.objects.filter(
        event=event,
        user=request.user
    ).first()
    
    if request.method == 'POST':
        form = EventFeedbackForm(request.POST, instance=existing_feedback)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.event = event
            feedback.user = request.user
            feedback.save()
            messages.success(request, 'Feedback submitted successfully.')
            return redirect('event:event_detail', pk=pk)
    else:
        form = EventFeedbackForm(instance=existing_feedback)
    
    return render(request, 'event_management/feedback_form.html', {
        'form': form,
        'event': event
    })

@login_required
def event_feedback_list(request, pk):
    event = get_object_or_404(Event, pk=pk)
    feedback = event.feedback.all()
    
    return render(request, 'event_management/feedback_list.html', {
        'event': event,
        'feedback': feedback
    })

@login_required
@user_passes_test(is_staff)
def event_resources(request, pk):
    event = get_object_or_404(Event, pk=pk)
    resources = event.resources.all()
    
    return render(request, 'event_management/resource_list.html', {
        'event': event,
        'resources': resources
    })

@login_required
@user_passes_test(is_staff)
def resource_add(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    if request.method == 'POST':
        form = EventResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.event = event
            resource.uploaded_by = request.user
            resource.save()
            messages.success(request, 'Resource added successfully.')
            return redirect('event:event_resources', pk=pk)
    else:
        form = EventResourceForm()
    
    return render(request, 'event_management/resource_form.html', {
        'form': form,
        'event': event
    })

@login_required
@user_passes_test(is_staff)
def resource_delete(request, pk):
    resource = get_object_or_404(EventResource, pk=pk)
    event_pk = resource.event.pk
    
    if request.method == 'POST':
        resource.delete()
        messages.success(request, 'Resource deleted successfully.')
        return redirect('event:event_resources', pk=event_pk)
    
    return render(request, 'event_management/resource_confirm_delete.html', {
        'resource': resource
    })

@login_required
def event_calendar(request):
    events = Event.objects.filter(
        is_public=True,
        start_date__gte=timezone.now()
    ).order_by('start_date')
    
    return render(request, 'event_management/event_calendar.html', {
        'events': events
    })

@login_required
@user_passes_test(is_staff)
def create_registration(request):
    if request.method == 'POST':
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.user = form.cleaned_data['user']
            registration.event = form.cleaned_data['event']
            registration.save()
            messages.success(request, 'Registration created successfully.')
            return redirect('event:my_registrations')
    else:
        form = EventRegistrationForm()
    
    return render(request, 'event_management/registration_form.html', {
        'form': form,
        'action': 'Create'
    }) 