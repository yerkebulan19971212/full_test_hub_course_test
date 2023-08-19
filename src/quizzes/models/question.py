from django.db import models

from src.common import abstract_models


class CommonQuestion(
    abstract_models.TimeStampedModel,
    # abstract_models.AbstractBaseNameCode
):
    name_code = models.CharField(
        max_length=255,
        # unique=True,
        null=True,
        blank=True
    )
    text = models.TextField(blank=True, null=True)
    file = models.FileField(blank=True, null=True)

    class Meta:
        db_table = 'quizz\".\"common_question'

    def __str__(self):
        if self.text:
            return str(self.text)
        return "None"


class Question(
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel
):
    common_question = models.ForeignKey(
        'quizzes.CommonQuestion',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        db_index=True
    )
    lesson_question_level = models.ForeignKey(
        'quizzes.LessonQuestionLevel',
        on_delete=models.CASCADE,
        db_index=True,
        related_name='questions'
    )
    question = models.TextField(null=True)
    math = models.BooleanField(default=False)
    variant = models.ForeignKey(
        'quizzes.Variant',
        on_delete=models.CASCADE,
        db_index=True
    )

    class Meta:
        db_table = 'quizz\".\"question'

    def __str__(self):
        return f'{self.question}'
