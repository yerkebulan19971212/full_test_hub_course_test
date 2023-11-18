# celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

celery_app = Celery('config', broker='redis://86.107.199.59:6379/12')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(7200.0, rating_quizz_full.s(),
                             name='add every 3600')


@celery_app.task
def rating_quizz_full():
    print('==========')
    from src.accounts.models import User
    from src.common.models import RatingTest, BoughtPacket, Packet
    from src.common.utils import get_monday_and_next_monday
    monday, next_monday = get_monday_and_next_monday()

    rating = RatingTest.objects.filter(
        start_time=monday,
        end_time=next_monday,
    )
    if not rating.exists():
        rating = RatingTest.objects.create(
            start_time=monday,
            end_time=next_monday,
        )
    else:
        rating = rating.first()
    packet = Packet.objects.filter(name_code='rating').first()
    users = User.objects.all()
    for u in users:
        bought_packet, created = BoughtPacket.objects.get_or_create(
            user=u,
            packet=packet,
            rating_test=rating,
            end_time=next_monday,
        )
        if created:
            print("created")
            bought_packet.start_time = monday
            bought_packet.remainder = 1
            bought_packet.price = 0
            bought_packet.save()
        else:
            print("not created")
