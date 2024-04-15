from django.db import models

from src.common import abstract_models


class CategoryQuerySet(abstract_models.AbstractQuerySet):
    pass


class CategoryAPIManager(abstract_models.AbstractManager):
    def all_active(self):
        return self.is_active().prefetch_related('children')


class Category(
    abstract_models.UUID,
    abstract_models.AbstractBaseName,
    abstract_models.AbstractBaseNameCode,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel,
    abstract_models.Description,
    abstract_models.Icon,
    abstract_models.Deleted
):
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='children',
        db_index=True
    )
    api_objects = CategoryAPIManager.from_queryset(CategoryQuerySet)()

    class Meta:
        db_table = 'course\".\"category'
