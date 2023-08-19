from django.db import models
from src.common import abstract_models


class CourseTypeQuerySet(abstract_models.AbstractQuerySet):
    pass


class CourseTypeManager(models.Manager):
    def get_ent(self):
        return self.get(name_code='ent')


class CourseType(
    abstract_models.UUID,
    abstract_models.AbstractBaseName,
    abstract_models.AbstractBaseNameCode,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel
):
    icon = models.FileField(upload_to='test_type', null=True, blank=True)

    objects = CourseTypeManager.from_queryset(CourseTypeQuerySet)()

    class Meta:
        db_table = 'common\".\"course_type'

    def __str__(self):
        return f"{self.name_code}"
