from django.db import models
from src.common import abstract_models
from src.common.constant import QuizzType, QuizzStatus, TestLang


class StudentAnswer(abstract_models.TimeStampedModel):
    student_quizz = models.ForeignKey(
        'quizzes.StudentQuizz',
        related_name='student_answers',
        on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        'quizzes.Question',
        related_name='student_answers',
        on_delete=models.CASCADE
    )
    answer = models.ForeignKey(
        'quizzes.Answer',
        on_delete=models.CASCADE,
        related_name='student_answers'
    )
    lesson = models.ForeignKey(
        'common.Lesson',
        on_delete=models.CASCADE,
        related_name='student_answers',
        null=True,
        db_index=True,
    )
    status = models.BooleanField(default=True)

    class Meta:
        db_table = 'quizz\".\"student_answer'

    def __str__(self):
        return f'{self.question}'


class StudentScore(abstract_models.TimeStampedModel):
    student_quizz = models.ForeignKey(
        'quizzes.StudentQuizz',
        related_name='question_score',
        db_index=True,
        on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        'quizzes.Question',
        related_name='question_score',
        db_index=True,
        on_delete=models.CASCADE
    )
    lesson = models.ForeignKey(
        'common.Lesson',
        on_delete=models.CASCADE,
        related_name='question_score',
        null=True,
        db_index=True,
    )
    score = models.IntegerField(default=0)
    status = models.BooleanField(default=True)

    class Meta:
        db_table = 'quizz\".\"student_score'

    def __str__(self):
        return f'{self.question}'


class TestFullScore(abstract_models.TimeStampedModel):
    student_quizz = models.ForeignKey(
        'quizzes.StudentQuizz',
        on_delete=models.CASCADE,
        related_name='test_full_score',
        db_index=True
    )
    lesson = models.ForeignKey(
        'common.Lesson',
        on_delete=models.CASCADE,
        related_name='test_full_score',
        db_index=True,
    )
    unattem = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    number_of_question = models.IntegerField(default=0)
    number_of_score = models.IntegerField(default=0)
    accuracy = models.IntegerField(default=0)

    class Meta:
        db_table = 'quizz\".\"test_full_score'
