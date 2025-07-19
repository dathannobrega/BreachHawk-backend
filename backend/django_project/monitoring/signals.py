from django.db.models.signals import post_save
from django.dispatch import receiver
from leaks.models import Leak
from .services import check_leak_against_resources


@receiver(post_save, sender=Leak)
def leak_created(sender, instance, created, **kwargs):
    if created:
        check_leak_against_resources(instance)
