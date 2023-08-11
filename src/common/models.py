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


class City(
    abstract_models.UUID,
    abstract_models.AbstractBaseName,
    abstract_models.AbstractBaseNameCode,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel
):
    country = models.ForeignKey(
        Country,
        related_name='cities',
        on_delete=models.CASCADE,
        db_index=True,
        null=True
    )

    class Meta:
        db_table = 'common\".\"city'

    def __str__(self):
        return f"{self.name_code}"


class KaspiPay(
    abstract_models.UUID,
    abstract_models.TimeStampedModel
):
    command = models.CharField(max_length=128)
    txn_id = models.CharField(max_length=128)
    account = models.CharField(max_length=128)
    txnDate = models.CharField(max_length=128, default="")
    price = models.FloatField()

    class Meta:
        db_table = 'integration\".\"kaspi_pay'

    def __str__(self):
        return f"{self.account} - {self.price}"
