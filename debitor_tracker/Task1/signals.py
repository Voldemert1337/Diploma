from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import NewUsers

@receiver(post_save, sender=NewUsers)
def check_subscription(sender, instance, **kwargs):
    if instance.subscription and instance.data_subscription and instance.data_subscription < timezone.now():
        instance.subscription = False
        instance.save()
