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
    course_type = models.ForeignKey(
        'common.CourseType',
        on_delete=models.CASCADE,
        null=True,
        db_index=True,
        related_name='lessons'
    )
    math = models.BooleanField(default=False)
    objects = LessonManager.from_queryset(LessonQuerySet)()

    class Meta:
        db_table = 'common\".\"lesson'

    def __str__(self):
        return f"{self.name_code}"
