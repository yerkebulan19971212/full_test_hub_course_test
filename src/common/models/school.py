from django.db import models
from src.common import abstract_models


class School(
    abstract_models.UUID,
    abstract_models.AbstractBaseName,
    abstract_models.AbstractBaseNameCode,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel
):
    city = models.ForeignKey(
        "common.City",
        related_name='schools',
        on_delete=models.CASCADE,
        db_index=True,
        null=True
    )

    class Meta:
        db_table = 'common\".\"school'

    def __str__(self):
        return f"{self.name_code}"
