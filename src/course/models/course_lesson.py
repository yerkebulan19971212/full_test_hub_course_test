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


class CourseLesson(
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
        related_name="course_lessons"
    )
    description = models.TextField(null=True)
    course_lesson_type = models.ForeignKey(
        CourseLessonType,
        on_delete=models.CASCADE,
        related_name="course_lessons"
    )
    from_course_lesson = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_index=True
    )

    class Meta:
        db_table = 'course\".\"course_lesson'

    def __str__(self):
        return f'{self.description}'


class CourseTopicLessonM2M(
    abstract_models.UUID,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel
):
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="course_topic_lessons_m2m"
    )
    course = models.ForeignKey(
        'course.CourseTopic',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="course_topic_lessons_m2m"
    )
    course_lesson = models.ForeignKey(
        'course.CourseLesson',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="course_topic_lessons_m2m"
    )

    class Meta:
        db_table = 'course\".\"course_topic_lesson_m2m'

    def __str__(self):
        return f'{self.course_lesson.name_ru}'
