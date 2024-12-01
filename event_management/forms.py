from django import forms
from django.utils import timezone
from .models import Event, EventRegistration, EventFeedback, EventResource, User

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'event_type', 'start_date', 'end_date',
            'location', 'capacity', 'registration_deadline', 'related_books',
            'featured_authors', 'image', 'attachment', 'is_public',
            'requires_registration', 'registration_fee'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter event title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter event description'
            }),
            'event_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter event location'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'registration_deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'related_books': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
            'featured_authors': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'requires_registration': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'registration_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        registration_deadline = cleaned_data.get('registration_deadline')

        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError(
                "End date must be after start date"
            )

        if registration_deadline and start_date and registration_deadline >= start_date:
            raise forms.ValidationError(
                "Registration deadline must be before event start date"
            )

        return cleaned_data

class EventRegistrationForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    event = forms.ModelChoiceField(
        queryset=Event.objects.filter(
            status='UPCOMING',
            requires_registration=True,
            registration_deadline__gt=timezone.now()
        ).exclude(
            registrations__status='CANCELLED'
        ),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = EventRegistration
        fields = ['user', 'event', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requirements or notes?'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['event'].queryset = Event.objects.filter(
            status='UPCOMING',
            requires_registration=True,
            registration_deadline__gt=timezone.now()
        ).exclude(
            registrations__status='CANCELLED'
        ).order_by('start_date')

    def clean(self):
        cleaned_data = super().clean()
        event = cleaned_data.get('event')
        user = cleaned_data.get('user')

        if event and user:
            # Check if user is already registered
            if EventRegistration.objects.filter(event=event, user=user).exists():
                raise forms.ValidationError("This user is already registered for this event.")
            
            # Check if event is full
            if event.is_full:
                raise forms.ValidationError("This event is already full.")

        return cleaned_data

class EventFeedbackForm(forms.ModelForm):
    class Meta:
        model = EventFeedback
        fields = ['rating', 'comment', 'is_anonymous']
        widgets = {
            'rating': forms.Select(attrs={
                'class': 'form-select'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your thoughts about the event'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class EventResourceForm(forms.ModelForm):
    class Meta:
        model = EventResource
        fields = ['title', 'description', 'resource_type', 'file', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter resource title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter resource description'
            }),
            'resource_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class EventSearchForm(forms.Form):
    SORT_CHOICES = [
        ('start_date', 'Date'),
        ('title', 'Title'),
        ('event_type', 'Event Type'),
    ]

    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search events...'
        })
    )
    event_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Event.EVENT_TYPES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Event.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    ) 