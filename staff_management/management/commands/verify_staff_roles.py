from django.core.management.base import BaseCommand
from staff_management.models import StaffMember

class Command(BaseCommand):
    help = 'Verifies staff member roles and shows current status'

    def handle(self, *args, **kwargs):
        staff_members = StaffMember.objects.all()
        
        self.stdout.write(self.style.NOTICE('Checking staff member roles...'))
        
        for staff_member in staff_members:
            self.stdout.write(
                f"Staff: {staff_member.user.get_full_name()} "
                f"(ID: {staff_member.employee_id}) "
                f"- Current Role: {staff_member.user.role}"
            ) 