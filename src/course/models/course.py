from django.db import models
from django.db.models import Count

from src.common import abstract_models


class CourseQuerySet(abstract_models.AbstractQuerySet):
    def content_count(self):
        return self.annotate(content_count=Count('course_topic_lessons_m2m2'))


class CourseManager(abstract_models.AbstractManager):
    pass


class CourseAPIManager(abstract_models.AbstractManager):
    def first_page(self):
        return self.is_active().content_count()


class Course(
    abstract_models.UUID,
    abstract_models.AbstractBaseName,
    abstract_models.AbstractBaseNameCode,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel,
    abstract_models.Deleted,
):
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="courses"
    )
    description = models.TextField(null=True)
    main_img = models.FileField()
    price = models.FloatField(default=0)
    from_course = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_index=True
    )

    objects = CourseManager.from_queryset(CourseQuerySet)()
    api_objects = CourseAPIManager.from_queryset(CourseQuerySet)()

    class Meta:
        db_table = 'course\".\"course'

    def __str__(self):
        return f'{self.description}'
