from django.db import models
from django.utils import timezone
from datetime import timedelta
from user_management.models import User

class MembershipPlan(models.Model):
    PLAN_CHOICES = [
        ('MONTHLY', 'Monthly'),
        ('YEARLY', 'Yearly'),
    ]

    name = models.CharField(max_length=50, unique=True)
    duration = models.CharField(max_length=10, choices=PLAN_CHOICES)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.get_duration_display()})"

    def active_members_count(self):
        """Returns the count of active members for this plan"""
        return self.membership_set.filter(is_active=True).count()

class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Log membership creation
            MemberActivity.objects.create(
                membership=self,
                activity_type='CREATE',
                description=f"Membership created with plan: {self.plan.name}"
            )
            
            # Create renewal reminder
            reminder_date = self.end_date - timedelta(days=7)
            RenewalReminder.objects.create(
                membership=self,
                reminder_date=reminder_date
            )
        else:
            # Log membership update
            MemberActivity.objects.create(
                membership=self,
                activity_type='UPDATE',
                description=f"Membership updated. Active status: {self.is_active}"
            )

    def record_activity(self, activity_type, description):
        """Helper method to record member activities"""
        return MemberActivity.objects.create(
            membership=self,
            activity_type=activity_type,
            description=description
        )

    def create_renewal_reminder(self, days_before=7):
        """Create a renewal reminder for the membership"""
        reminder_date = self.end_date - timedelta(days=days_before)
        return RenewalReminder.objects.create(
            membership=self,
            reminder_date=reminder_date
        )

    def is_expiring_soon(self, days=7):
        """Check if membership is expiring within specified days"""
        if self.is_active:
            days_until_expiry = (self.end_date - timezone.now().date()).days
            return 0 <= days_until_expiry <= days
        return False

class MemberActivity(models.Model):
    ACTIVITY_TYPES = [
        ('CREATE', 'Membership Created'),
        ('UPDATE', 'Membership Updated'),
        ('RENEW', 'Membership Renewed'),
        ('EXPIRE', 'Membership Expired'),
        ('CANCEL', 'Membership Cancelled'),
        ('PAYMENT', 'Payment Recorded'),
    ]

    membership = models.ForeignKey(
        Membership, 
        on_delete=models.CASCADE, 
        related_name='activities'
    )
    activity_type = models.CharField(
        max_length=20, 
        choices=ACTIVITY_TYPES,
        default='CREATE'
    )
    activity_date = models.DateTimeField(default=timezone.now)
    description = models.TextField()

    class Meta:
        ordering = ['-activity_date']
        verbose_name_plural = 'Member Activities'

    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.membership.user.username}"

class RenewalReminder(models.Model):
    membership = models.ForeignKey(
        Membership, 
        on_delete=models.CASCADE, 
        related_name='renewal_reminders'
    )
    reminder_date = models.DateTimeField()
    sent = models.BooleanField(default=False)
    sent_date = models.DateTimeField(null=True, blank=True)
    response = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('RENEWED', 'Renewed'),
            ('DECLINED', 'Declined'),
            ('NO_RESPONSE', 'No Response')
        ],
        default='PENDING'
    )

    class Meta:
        ordering = ['reminder_date']

    def __str__(self):
        return f"Reminder for {self.membership.user.username} on {self.reminder_date}"

    def mark_as_sent(self):
        """Mark reminder as sent"""
        self.sent = True
        self.sent_date = timezone.now()
        self.save()

    def update_response(self, response):
        """Update member's response to renewal reminder"""
        self.response = response
        self.save() 