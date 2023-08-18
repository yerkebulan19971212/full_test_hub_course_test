from django.db import models
from src.common import abstract_models


class CourseType(
    abstract_models.UUID,
    abstract_models.AbstractBaseName,
    abstract_models.AbstractBaseNameCode,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel
):
    icon = models.FileField(upload_to='test_type', null=True, blank=True)

    class Meta:
        db_table = 'common\".\"course_type'

    def __str__(self):
        return f"{self.name_code}"
