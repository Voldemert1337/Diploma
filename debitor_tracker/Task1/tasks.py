from celery import shared_task
from django.utils import timezone
from .models import Users

@shared_task
def check_user_subscriptions():
    users = Users.objects.filter(subscription=True, data_subscription__lt=timezone.now())
    for user in users:
        user.subscription = False
        user.save()
