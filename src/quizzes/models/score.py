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
    status = models.BooleanField(default=True)

    class Meta:
        db_table = 'quizz\".\"student_answer'

    def __str__(self):
        return f'{self.question}'


class StudentScore(abstract_models.TimeStampedModel):
    student_quizz = models.ForeignKey(
        'quizzes.StudentQuizz',
        related_name='question_score',
        on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        'quizzes.Question',
        related_name='question_score',
        on_delete=models.CASCADE
    )
    score = models.IntegerField(default=0)
    status = models.BooleanField(default=True)

    class Meta:
        db_table = 'quizz\".\"student_score'

    def __str__(self):
        return f'{self.question}'
