from django.db import models

from src.common import abstract_models
from src.common.constant import PromoCodeType


class PromoCode(
    abstract_models.UUID,
    abstract_models.AbstractBaseNameCode,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel
):
    bonus = models.IntegerField(default=100)
    promo_type = models.CharField(
        max_length=11,
        choices=PromoCodeType.choices(),
        default=PromoCodeType.ORDINARY
    )
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        db_table = 'common\".\"promo_code'

    def __str__(self):
        return f"{self.name_code}"


class UserPromoCode(
    abstract_models.UUID,
    abstract_models.TimeStampedModel
):
    promo_code = models.ForeignKey(
        PromoCode,
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE
    )
    balance = models.IntegerField(default=0)

    class Meta:
        db_table = 'common\".\"use_promo_code'

    def __str__(self):
        return f"{self.name_code}"
