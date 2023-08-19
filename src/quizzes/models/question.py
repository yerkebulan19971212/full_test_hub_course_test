from django.db import models
from django.db.models import Prefetch

from src.common import abstract_models
from src.common.constant import ChoiceType
from src.quizzes import models as quizzes_models


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


class QuestionQuerySet(abstract_models.AbstractQuerySet):

    def get_questions_for_flash_card(self, lang: str, lesson: int,
                                     question_number: int):
        return self.filter(
            variant__language=lang,
            lesson_question_level__test_type_lesson__lesson_id=lesson,
            lesson_question_level__question_level__choice=ChoiceType.CHOICE
        )[:question_number]

    def get_questions_with_answer(self):
        return self.prefetch_related(
            Prefetch('answers', queryset=quizzes_models.Answer.objects.all()))


class QuestionManager(models.Manager):
    pass


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

    objects = QuestionManager.from_queryset(QuestionQuerySet)()

    class Meta:
        db_table = 'quizz\".\"question'

    def __str__(self):
        return f'{self.question}'
