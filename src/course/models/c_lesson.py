from django.db import models

from src.common import abstract_models


class CourseLessonType(
    abstract_models.UUID,
    abstract_models.AbstractBaseName,
    abstract_models.AbstractBaseNameCode,
    abstract_models.Description,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.Icon,
    abstract_models.TimeStampedModel,
    abstract_models.Deleted
):
    pass


class CLesson(
    abstract_models.UUID,
    abstract_models.AbstractBaseNameCode,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.Description,
    abstract_models.TimeStampedModel,
    abstract_models.Deleted
):
    title = models.CharField(max_length=1024, default='', blank=True)
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="c_lessons"
    )
    duration = models.DurationField(null=True, blank=True)
    img = models.FileField(null=True)
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


class CLessonContent(
    abstract_models.UUID,
    abstract_models.AbstractBaseName,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel,
    abstract_models.Deleted
):
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="c_lesson_content"
    )
    text = models.TextField(null=True)
    video = models.URLField(null=True)
    img = models.FileField(null=True)
    file = models.FileField(null=True)
    course_lesson = models.ForeignKey(
        CLesson,
        on_delete=models.CASCADE,
        related_name="c_lesson_content"
    )

    class Meta:
        db_table = 'course\".\"c_lesson_content'

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


class UserCLesson(
    abstract_models.UUID,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel
):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        db_index=True,
        related_name='user_c_lesson'
    )
    course_lesson = models.ForeignKey(
        CLesson,
        on_delete=models.CASCADE,
        db_index=True,
        related_name='user_c_lesson'
    )
    passed = models.BooleanField(default=False)
    passed_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'course\".\"user_course_lesson'

    def __str__(self):
        return f'{self.course_lesson.name_ru}'
