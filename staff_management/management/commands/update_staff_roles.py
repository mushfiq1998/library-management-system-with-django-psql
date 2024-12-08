from django.core.management.base import BaseCommand
from staff_management.models import StaffMember

class Command(BaseCommand):
    help = 'Updates all staff member user accounts to have the STAFF role'

    def handle(self, *args, **kwargs):
        staff_members = StaffMember.objects.all()
        updated_count = 0

        for staff_member in staff_members:
            if staff_member.user.role != 'STAFF':
                staff_member.user.role = 'STAFF'
                staff_member.user.save()
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {updated_count} user roles to STAFF'
            )
        ) 