from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import datetime, date
from user_management.models import User

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class StaffMember(models.Model):
    EMPLOYMENT_STATUS = [
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract'),
        ('INTERN', 'Intern'),
    ]

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='staff_profile'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name='staff_members'
    )
    employee_id = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                regex='^EMP\d{7}$',
                message='Employee ID must be in format EMP followed by 7 digits'
            )
        ]
    )
    designation = models.CharField(max_length=100)
    employment_status = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_STATUS,
        default='FULL_TIME'
    )
    joining_date = models.DateField()
    phone_number = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    emergency_contact = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    address = models.TextField()
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id}"

    def save(self, *args, **kwargs):
        if not self.employee_id:
            # Generate employee ID if not provided
            last_emp = StaffMember.objects.order_by('-employee_id').first()
            if last_emp:
                last_num = int(last_emp.employee_id[3:])
                new_num = last_num + 1
            else:
                new_num = 1
            self.employee_id = f'EMP{new_num:07d}'
        super().save(*args, **kwargs)

class Leave(models.Model):
    LEAVE_TYPE = [
        ('ANNUAL', 'Annual Leave'),
        ('SICK', 'Sick Leave'),
        ('EMERGENCY', 'Emergency Leave'),
        ('UNPAID', 'Unpaid Leave'),
    ]

    STATUS = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]

    staff_member = models.ForeignKey(
        StaffMember,
        on_delete=models.CASCADE,
        related_name='leaves'
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='PENDING'
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves'
    )
    approved_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.staff_member.user.get_full_name()} - {self.leave_type}"

    @property
    def duration(self):
        return (self.end_date - self.start_date).days + 1

class Attendance(models.Model):
    staff_member = models.ForeignKey(
        StaffMember,
        on_delete=models.CASCADE,
        related_name='attendance'
    )
    date = models.DateField()
    check_in = models.TimeField()
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PRESENT', 'Present'),
            ('ABSENT', 'Absent'),
            ('HALF_DAY', 'Half Day'),
            ('LATE', 'Late'),
        ],
        default='PRESENT'
    )
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['staff_member', 'date']

    def __str__(self):
        return f"{self.staff_member.user.get_full_name()} - {self.date}"

    @property
    def duration(self):
        if self.check_out:
            time_diff = datetime.combine(date.min, self.check_out) - datetime.combine(date.min, self.check_in)
            return time_diff.total_seconds() / 3600  # Return hours
        return None 