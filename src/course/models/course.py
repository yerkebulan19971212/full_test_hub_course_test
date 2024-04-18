from django.db import models
from django.db.models import Count

from src.common import abstract_models
from src.common.constant import TestLang


class CourseQuerySet(abstract_models.AbstractQuerySet):
    def content_count(self):
        return self.annotate(content_count=Count('course_topic'))


class CourseManager(abstract_models.AbstractManager):
    pass


class CourseAPIManager(abstract_models.AbstractManager):
    def all_active(self):
        return self.is_active()

    def first_page(self):
        return self.is_active().content_count()


class Course(
    abstract_models.UUID,
    abstract_models.AbstractBaseNameCode,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel,
    abstract_models.Deleted,
):
    title = models.CharField(max_length=1024, default='', blank=True)
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="courses"
    )
    teacher = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        null=True, blank=True,
    )
    language = models.CharField(
        max_length=64,
        choices=TestLang.choices(),
        default=TestLang.KAZAKH,
        db_index=True
    )
    description = models.TextField(null=True)
    main_img = models.FileField()
    price = models.FloatField(default=0)
    discount_price = models.FloatField(default=0)
    discount_percent = models.FloatField(default=0)
    number_of_students = models.FloatField(default=0)
    course_trailer = models.URLField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    category = models.ForeignKey(
        'course.Category',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        db_index=True,
        related_name="courses"
    )
    from_course = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_index=True,
        related_name="children"
    )

    objects = CourseManager.from_queryset(CourseQuerySet)()
    api_objects = CourseAPIManager.from_queryset(CourseQuerySet)()

    class Meta:
        db_table = 'course\".\"course'

    # def __str__(self):
    #     return f'{self.name_code}'
