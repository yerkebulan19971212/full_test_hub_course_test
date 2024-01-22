from django.db import models

from src.common import abstract_models


class Support(
    abstract_models.UUID,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel
):
    question = models.ForeignKey(
        "quizzes.Question",
        on_delete=models.CASCADE,
        related_name="supports"
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="supports"
    )
    comment = models.TextField()

    class Meta:
        db_table = 'common\".\"support'
