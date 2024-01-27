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
    main_img = models.FileField()

    class Meta:
        db_table = 'course\".\"course'

    def __str__(self):
        return f'{self.description}'

