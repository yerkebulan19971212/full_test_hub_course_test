from django.db import models

from src.accounts.models import User
from src.common import abstract_models


class BlogCategory(abstract_models.AbstractBaseNameCode):
    pass


class Blog(
    abstract_models.UUID,
    abstract_models.AbstractBaseNameCode,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel,
    abstract_models.Description
):
    title = models.CharField(max_length=1024)
    views = models.PositiveIntegerField(default=0)
    duration_length = models.CharField(max_length=1024)
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.CASCADE,
        related_name='blogs',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blogs',
    )

    class Meta:
        db_table = 'common\".\"blog'

    def __str__(self):
        return f"{self.name_code}"
