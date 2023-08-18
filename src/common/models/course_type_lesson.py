from django.db import models
from src.common import abstract_models


class CourseTypeLesson(
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
        related_name='course_type_lessons',
    )
    lesson = models.ForeignKey(
        'common.Lesson',
        on_delete=models.CASCADE,
        null=True,
        db_index=True,
        related_name='course_type_lessons'
    )

    class Meta:
        db_table = 'common\".\"course_type_lesson'

    def __str__(self):
        return f"{self.name_code}"
