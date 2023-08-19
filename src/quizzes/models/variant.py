from django.db import models
from src.common import abstract_models
from src.common.constant import TestLang


class Variant(
    abstract_models.UUID,
    abstract_models.AbstractBaseName,
    abstract_models.AbstractBaseNameCode,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel
):
    course_type = models.ForeignKey(
        'common.CourseType',
        on_delete=models.CASCADE,
        null=True,
        db_index=True,
        related_name='variants'
    )
    language = models.CharField(
        max_length=64,
        choices=TestLang.choices(),
        default=TestLang.KAZAKH,
        db_index=True
    )
    variant_title = models.IntegerField()

    class Meta:
        db_table = 'quizz\".\"variant'

    def __str__(self):
        return f"{self.name_code}"


class VariantQuestion(
    abstract_models.UUID,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel
):
    question = models.ForeignKey(
        'quizzes.Question',
        on_delete=models.CASCADE,
        null=True,
        db_index=True,
        related_name='variant_questions'
    )
    variant = models.ForeignKey(
        'quizzes.Variant',
        on_delete=models.CASCADE,
        null=True,
        db_index=True,
        related_name='variant_questions'
    )

    class Meta:
        db_table = 'quizz\".\"variant_question'

    def __str__(self):
        return f"{self.variant.name_code}"
