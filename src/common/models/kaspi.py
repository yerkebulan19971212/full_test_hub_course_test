from django.db import models
from src.common import abstract_models


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






