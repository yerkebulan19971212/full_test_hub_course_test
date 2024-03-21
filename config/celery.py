# celery.py
from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from django.db.models import F
from django.utils import timezone

from src.common.constant import QuizzStatus

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

celery_app = Celery('config', broker='redis://:yerke1234@185.125.90.25:6379/0')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(7200.0, rating_quizz_full.s(), name='add every 3600')
    sender.add_periodic_task(3600.0, auto_complete_finish_test.s(), name='auto complete every 3600')
    sender.add_periodic_task(60, add_balance_to_student.s(), name='add_balance_to_student')


@celery_app.task
def rating_quizz_full():
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
    packet = Packet.objects.filter(name_code='rating', is_active=True).first()
    if packet is not None:
        users = User.objects.all()
        for u in users:
            bought_packet, created = BoughtPacket.objects.get_or_create(
                user=u,
                packet=packet,
                rating_test=rating,
                end_time=next_monday,
            )
            if created:
                bought_packet.start_time = monday
                bought_packet.remainder = 1
                bought_packet.price = 0
                bought_packet.save()
            else:
                print("not created")


@celery_app.task
def finish_test(student_quizz_id):
    from src.services.utils import finish_full_test
    finish_full_test(student_quizz_id=student_quizz_id)


@celery_app.task
def auto_complete_finish_test():
    from src.services.utils import finish_full_test
    from src.quizzes.models import (StudentQuizz)
    current_time = timezone.now()
    student_quizzes = StudentQuizz.objects.filter(
        status__in=[QuizzStatus.CONTINUE, QuizzStatus.NOT_PASSED],
        quizz_start_time__lt=current_time - F('quizz_duration')
    )
    for s in student_quizzes:
        finish_full_test(student_quizz_id=s.id)


@celery_app.task
def add_balance_to_student():
    from src.services.utils import add_balance
    add_balance()


@celery_app.task
def student_user_question_count(user, question_ids, quizz_type):
    from src.quizzes.models import UserQuestionCount, Question
    questions = Question.objects.filter(id__in=question_ids)
    user_questions = UserQuestionCount.objects.filter(
        user_id=user,
        question_id__in=question_ids,
        quizz_type_id=quizz_type
    )
    user_question_ids = [q.question_id for q in user_questions]
    UserQuestionCount.objects.bulk_create([
        UserQuestionCount(
            user_id=user,
            quizz_type_id=quizz_type,
            question=q,
        ) for q in questions.exclud(id__in=user_question_ids)
    ])
    UserQuestionCount.objects.filter(
        user_id=user,
        question_id__in=question_ids,
        quizz_type_id=quizz_type
    ).update(quantity=F('quantity') + 1)
