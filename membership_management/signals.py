from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Membership, MemberActivity

@receiver(pre_save, sender=Membership)
def handle_membership_status(sender, instance, **kwargs):
    try:
        old_instance = Membership.objects.get(pk=instance.pk)
        # Check if membership has expired
        if old_instance.is_active and not instance.is_active:
            MemberActivity.objects.create(
                membership=instance,
                activity_type='EXPIRE',
                description='Membership expired'
            )
    except Membership.DoesNotExist:
        pass  # New instance, no need to check 