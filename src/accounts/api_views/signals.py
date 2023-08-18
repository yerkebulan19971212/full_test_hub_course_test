from src.oauth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime

from src.quizzes.models import StudentTest, Variant

#
# @receiver(post_save, sender=User)
# def create_variant_schedule(sender, instance, created, **kwargs):
#     if created:
#         variants = Variant.objects.all().order_by('?')
#         if variants.exists():
#             student_test_bulk = []
#             for variant in variants:
#                 student_test_bulk.append(
#                     StudentTest(
#                         user=instance,
#                         variant=variant,
#                         start_time=datetime.datetime.now(),
#                         student_test_group=None,
#                         end_time=datetime.datetime(2030, 5, 17),
#                         lessons=instance.lesson_pair,
#                         status="NOT_PASSED"
#                     )
#                 )
#             StudentTest.objects.bulk_create(student_test_bulk)
