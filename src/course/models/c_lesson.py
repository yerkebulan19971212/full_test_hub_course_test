from django.db import models

from src.common import abstract_models


class CourseLessonType(
    abstract_models.UUID,
    abstract_models.AbstractBaseNameCode,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel,
    abstract_models.Deleted
):
    icon = models.FileField()


class CLesson(
    abstract_models.UUID,
    abstract_models.AbstractBaseName,
    abstract_models.AbstractBaseNameCode,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel,
    abstract_models.Deleted
):
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="c_lessons"
    )
    description = models.TextField(null=True)
    course_lesson_type = models.ForeignKey(
        CourseLessonType,
        on_delete=models.CASCADE,
        related_name="c_lessons"
    )
    from_course_lesson = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_index=True
    )

    class Meta:
        db_table = 'course\".\"c_lessons'

    def __str__(self):
        return f'{self.name_code}'


class CourseTopicLesson(
    abstract_models.UUID,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel
):
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="course_topic_lessons"
    )
    course_topic = models.ForeignKey(
        'course.CourseTopic',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="course_topic_lessons"
    )
    course_lesson = models.ForeignKey(
        'course.CLesson',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="course_topic_lessons"
    )

    class Meta:
        db_table = 'course\".\"course_topic_lesson'

    def __str__(self):
        return f'{self.course_lesson.name_ru}'
