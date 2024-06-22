from django.db import models
from src.common import abstract_models
from src.common.constant import ChoiceType


class QuestionLevel(
    abstract_models.UUID,
    abstract_models.AbstractBaseNameCode,
    abstract_models.IsActive,
    abstract_models.Ordering,
    abstract_models.TimeStampedModel
):
    point = models.PositiveSmallIntegerField(default=0, db_index=True)
    choice = models.IntegerField(
        # choices=ChoiceType.choices(),
        default=0,
        db_index=True
    )

    class Meta:
        db_table = 'quizz\".\"question_level'

    def __str__(self):
        return f'{self.name_code}'


class LessonQuestionLevel(
    abstract_models.UUID,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel
):
    test_type_lesson = models.ForeignKey(
        'common.CourseTypeLesson',
        on_delete=models.CASCADE,
        db_index=True,
        related_name='lesson_question_level'
    )
    question_level = models.ForeignKey(
        'quizzes.QuestionLevel',
        on_delete=models.CASCADE,
        db_index=True,
        related_name='lesson_question_level'
    )
    number_of_questions = models.IntegerField(default=0, db_index=True)

    class Meta:
        db_table = 'quizz\".\"lesson_question_level'
        unique_together = ['test_type_lesson', 'question_level']

    def __str__(self):
        return f'{self.test_type_lesson.lesson.name_kz} - {self.question_level}'
