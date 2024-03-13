from django.db import models

from src.common import abstract_models


class Topic(
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
        related_name="course_topics"
    )
    description = models.TextField(null=True)
    from_course_topic = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_index=True
    )

    class Meta:
        db_table = 'course\".\"topic'

    def __str__(self):
        return f'{self.description}'


class CourseTopic(
    abstract_models.UUID,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel,
    abstract_models.Deleted
):
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="course_topic"
    )
    course = models.ForeignKey(
        'course.Course',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="course_topic"
    )
    topic = models.ForeignKey(
        'course.Topic',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="course_topic"
    )

    class Meta:
        db_table = 'course\".\"course_topic'

    def __str__(self):
        return f'{self.topic.name_code}'
