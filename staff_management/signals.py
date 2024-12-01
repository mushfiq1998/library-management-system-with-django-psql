from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from user_management.models import User
from .models import StaffMember, Department

# Comment out or remove these signals since we're handling creation in the form
# @receiver(post_save, sender=User)
# def create_staff_profile(sender, instance, created, **kwargs):
#     if created and instance.role == 'STAFF':
#         # Get default department or create one
#         default_dept, _ = Department.objects.get_or_create(
#             name='General',
#             defaults={'description': 'Default department for staff members'}
#         )
        
#         StaffMember.objects.create(
#             user=instance,
#             department=default_dept,
#             designation='Staff Member',
#             employment_status='FULL_TIME',
#             joining_date=timezone.now().date()
#         )

# @receiver(post_save, sender=User)
# def save_staff_profile(sender, instance, **kwargs):
#     if instance.role == 'STAFF':
#         try:
#             instance.staff_profile.save()
#         except StaffMember.DoesNotExist:
#             # Create staff profile if it doesn't exist
#             default_dept, _ = Department.objects.get_or_create(
#                 name='General',
#                 defaults={'description': 'Default department for staff members'}
#             )
            
#             StaffMember.objects.create(
#                 user=instance,
#                 department=default_dept,
#                 designation='Staff Member',
#                 employment_status='FULL_TIME',
#                 joining_date=timezone.now().date()
#             )