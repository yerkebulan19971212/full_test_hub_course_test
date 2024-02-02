from django.db.models import Max
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from src.accounts.models import User, BalanceHistory


@receiver(post_save, sender=User)
def create_user_topic_bulk(sender, instance, created, **kwargs):
    if created:
        user = User.objects.all().aggregate(max_user_id=Max('user_id'))
        instance.user_id = user.get('max_user_id') + 1
        instance.save()


@receiver(post_save, sender=BalanceHistory)
def add_balance(sender, instance, created, **kwargs):
    if created:
        user = instance.student
        user.balance = user.balance + instance.balance
        user.save()
