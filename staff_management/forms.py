from django import forms
from .models import StaffMember, Department, Leave, Attendance
from user_management.models import User
from django.utils import timezone
from django.db import transaction

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class StaffMemberForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = StaffMember
        fields = [
            'first_name', 'last_name', 'email', 'department', 'designation',
            'employment_status', 'joining_date', 'phone_number',
            'emergency_contact', 'address', 'salary'
        ]
        widgets = {
            'joining_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'employment_status': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'salary': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not self.instance.pk:  # Only check on create, not update
            try:
                user = User.objects.get(email=email)
                if hasattr(user, 'staff_profile'):
                    raise forms.ValidationError("This email is already associated with a staff member.")
            except User.DoesNotExist:
                pass
        return email

    @transaction.atomic
    def save(self, commit=True):
        email = self.cleaned_data.get('email')
        
        if self.instance.pk:
            # Update existing user
            user = self.instance.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = email
            user.save()
        else:
            # Try to get existing user or create new one
            try:
                user = User.objects.get(email=email)
                if hasattr(user, 'staff_profile'):
                    raise forms.ValidationError("This user already has a staff profile.")
            except User.DoesNotExist:
                # Create new user with unique username
                base_username = email.split('@')[0]
                username = base_username
                counter = 1
                
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    password=User.objects.make_random_password(),
                    first_name=self.cleaned_data['first_name'],
                    last_name=self.cleaned_data['last_name'],
                    email=email,
                    role='STAFF'
                )
            
        # Create staff member
        staff_member = super().save(commit=False)
        staff_member.user = user
        
        if commit:
            staff_member.save()
        
        return staff_member

class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Please provide a detailed reason for your leave request'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError("End date cannot be before start date")
            
            # Check if dates are in the past
            if start_date < timezone.now().date():
                raise forms.ValidationError("Start date cannot be in the past")
        
        return cleaned_data

class LeaveActionForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        new_status = cleaned_data.get('status')
        
        # Prevent changing from approved/rejected status
        if self.instance.pk and self.instance.status in ['APPROVED', 'REJECTED']:
            if new_status != self.instance.status:
                raise forms.ValidationError(
                    "Cannot change status of an already approved or rejected leave request"
                )
        
        return cleaned_data

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['staff_member', 'date', 'check_in', 'check_out', 'status', 'notes']
        widgets = {
            'staff_member': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_in': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'check_out': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        } 