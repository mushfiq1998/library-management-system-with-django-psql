from django import forms
from .models import Membership, MembershipPlan, MemberActivity, RenewalReminder

class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ['user', 'plan', 'start_date', 'end_date', 'is_active']
        widgets = {
            'user': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'plan': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch'
            })
        }

class MembershipPlanForm(forms.ModelForm):
    class Meta:
        model = MembershipPlan
        fields = ['name', 'duration', 'price']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter plan name',
                'required': True
            }),
            'duration': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01',
                'required': True
            })
        }

class MemberActivityForm(forms.ModelForm):
    class Meta:
        model = MemberActivity
        fields = ['membership', 'activity_type', 'description']
        widgets = {
            'membership': forms.Select(attrs={'class': 'form-select'}),
            'activity_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            })
        }

class RenewalReminderForm(forms.ModelForm):
    class Meta:
        model = RenewalReminder
        fields = ['membership', 'reminder_date', 'response']
        widgets = {
            'membership': forms.Select(attrs={'class': 'form-select'}),
            'reminder_date': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local'
                }
            ),
            'response': forms.Select(attrs={'class': 'form-select'})
        } 