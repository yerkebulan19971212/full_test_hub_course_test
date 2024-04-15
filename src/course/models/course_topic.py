from django.db import models

from src.common import abstract_models


class Topic(
    abstract_models.UUID,
    abstract_models.AbstractBaseNameCode,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.Description,
    abstract_models.TimeStampedModel
):
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="course_topics"
    )
    title = models.CharField(max_length=1024, default='', blank=True)
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


class CourseTopicQuerySet(abstract_models.AbstractQuerySet):
    pass


class CourseTopicAPIManager(abstract_models.AbstractManager):
    def all_active(self):
        return self.is_active()

    def ordering(self):
        self.all_active().order_by('order')


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
    objects = models.Manager.from_queryset(models.QuerySet)()
    api_objects = CourseTopicAPIManager.from_queryset(CourseTopicQuerySet)()

    class Meta:
        db_table = 'course\".\"course_topic'

    def __str__(self):
        return f'{self.topic.name_code}'
