from django.db import models

from src.common import abstract_models


class Course(
    abstract_models.UUID,
    abstract_models.AbstractBaseName,
    abstract_models.AbstractBaseNameCode,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel
):
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="courses"
    )
    description = models.TextField(null=True)

    class Meta:
        db_table = 'course\".\"course'

    def __str__(self):
        return f'{self.description}'


class CourseLesson(
    abstract_models.UUID,
    abstract_models.AbstractBaseTitle,
    abstract_models.AbstractBaseNameCode,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel
):
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="courses"
    )
    description = models.TextField(null=True)

    class Meta:
        db_table = 'course\".\"course_lesson'

    def __str__(self):
        return f'{self.description}'


class CourseLessonM2M(
    abstract_models.UUID,
    abstract_models.AbstractBaseTitle,
    abstract_models.AbstractBaseNameCode,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel
):
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="course_lessons_m2m2"
    )
    course = models.ForeignKey(
        'course.Course',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="course_lessons_m2m2"
    )
    course_lesson = models.ForeignKey(
        'course.CourseLesson',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="course_lessons_m2m2"
    )
    description = models.TextField(null=True)

    class Meta:
        db_table = 'course\".\"course_lesson_m2m'

    def __str__(self):
        return f'{self.description}'
