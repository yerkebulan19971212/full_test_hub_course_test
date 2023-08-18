from django.db import models
from src.common import abstract_models


class Country(
    abstract_models.UUID,
    abstract_models.AbstractBaseName,
    abstract_models.AbstractBaseNameCode,
    abstract_models.IsActive,
    abstract_models.Ordering,
    abstract_models.TimeStampedModel
):
    icon = models.FileField(upload_to='country')

    class Meta:
        db_table = 'common\".\"country'

    def __str__(self):
        return f' {self.name_ru}'
