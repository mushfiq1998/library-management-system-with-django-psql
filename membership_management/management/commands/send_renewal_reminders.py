from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from membership_management.models import RenewalReminder

class Command(BaseCommand):
    help = 'Send renewal reminders to members'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        # Get unsent reminders that are due
        reminders = RenewalReminder.objects.filter(
            sent=False,
            reminder_date__lte=now
        )

        for reminder in reminders:
            try:
                # Send email reminder
                send_mail(
                    subject='Membership Renewal Reminder',
                    message=f"""
                    Dear {reminder.membership.user.get_full_name()},

                    Your membership plan "{reminder.membership.plan.name}" is expiring on {reminder.membership.end_date}.
                    Please renew your membership to continue enjoying our services.

                    Best regards,
                    Library Team
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[reminder.membership.user.email],
                )

                # Mark reminder as sent
                reminder.mark_as_sent()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully sent reminder to {reminder.membership.user.email}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to send reminder to {reminder.membership.user.email}: {str(e)}'
                    )
                ) 