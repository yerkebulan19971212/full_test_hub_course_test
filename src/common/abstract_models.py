import uuid

from django.db import models


class UUID(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    `created`` and ``modified`` fields.
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Ordering(models.Model):
    order = models.IntegerField(default=1, db_index=True)

    class Meta:
        abstract = True


class IsActive(models.Model):
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True


class AbstractBaseName(models.Model):
    name_kz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)

    class Meta:
        abstract = True


class AbstractBaseNameCode(models.Model):
    name_code = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )

    class Meta:
        abstract = True


class AbstractBaseTitle(models.Model):
    title_kz = models.CharField(max_length=255)
    title_ru = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)

    class Meta:
        abstract = True


class AbstractQuerySet(models.QuerySet):

    def get_all_active(self):
        return self.filter(is_active=True)
