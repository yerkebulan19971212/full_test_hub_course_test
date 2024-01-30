from django.db import models

from src.common import abstract_models


class AnswerSign(
    abstract_models.AbstractBaseNameCode,
    abstract_models.IsActive,
    abstract_models.Ordering,
    abstract_models.TimeStampedModel
):
    pass

    class Meta:
        db_table = 'quizz\".\"answer_sign'

    def __str__(self):
        return f'{self.name_code}'


class Answer(
    abstract_models.TimeStampedModel,
    abstract_models.Ordering
):
    question = models.ForeignKey(
        'quizzes.Question',
        related_name='answers',
        on_delete=models.CASCADE,
        db_index=True,
    )
    answer = models.TextField()
    correct = models.BooleanField(default=False)
    math = models.BooleanField(default=False)
    answer_sign = models.ForeignKey(
        'quizzes.AnswerSign',
        related_name='answers',
        on_delete=models.CASCADE,
        db_index=True
    )

    class Meta:
        db_table = 'quizz\".\"answer'

    def __str__(self):
        return f'{self.question} - {self.answer}'
