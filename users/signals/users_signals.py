from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.conf import settings

User = settings.AUTH_USER_MODEL

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def assign_admin_group(sender, instance, created, **kwargs):
    if created and (instance.is_superuser):
        admin_group, _ = Group.objects.get_or_create(name='admin')
        instance.groups.add(admin_group)
