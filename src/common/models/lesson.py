from django.db import models
from src.common import abstract_models


class LessonQuerySet(abstract_models.AbstractQuerySet):
    pass


class LessonManager(models.Manager):
    pass


class Lesson(
    abstract_models.UUID,
    abstract_models.AbstractBaseName,
    abstract_models.AbstractBaseNameCode,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel
):
    # course_type = models.ForeignKey(
    #     'common.CourseType',
    #     on_delete=models.CASCADE,
    #     null=True,
    #     db_index=True,
    #     related_name='lessons'
    # )
    icon = models.FileField(upload_to='lesson', null=True, blank=True)
    choose_icon = models.FileField(upload_to='lesson/choose', null=True,
                                   blank=True)
    math = models.BooleanField(default=False)
    objects = LessonManager.from_queryset(LessonQuerySet)()

    class Meta:
        db_table = 'common\".\"lesson'

    def __str__(self):
        return f"{self.name_ru}"


class LessonPair(
    abstract_models.UUID,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel
):
    icon = models.ImageField(
        upload_to='lesson_images',
        blank=True,
        null=True
    )
    lesson_1 = models.ForeignKey(
        'common.Lesson',
        related_name='lesson_1',
        on_delete=models.CASCADE
    )
    lesson_2 = models.ForeignKey(
        'common.Lesson',
        on_delete=models.CASCADE,
        related_name='lesson_2',
        blank=True,
        null=True,
    )

    class Meta:
        db_table = 'common\".\"lesson_pair'

    def __str__(self):
        return f'{self.lesson_1.name_ru} - {self.lesson_2.name_ru if self.lesson_2 else ""}'
