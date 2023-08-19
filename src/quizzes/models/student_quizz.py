from django.db import models
from src.common import abstract_models
from src.common.constant import QuizzType, QuizzStatus


class StudentQuizz(
    abstract_models.UUID,
    abstract_models.TimeStampedModel
):
    user = models.ForeignKey(
        'accounts.User',
        related_name='student_quizzes',
        on_delete=models.CASCADE
    )
    course_type = models.ForeignKey(
        'common.CourseType',
        on_delete=models.CASCADE,
        db_index=True,
        related_name='student_quizzes'
    )
    status = models.CharField(
        max_length=12,
        choices=QuizzStatus.choices(),
        default=QuizzStatus.NOT_PASSED
    )
    lesson = models.ForeignKey(
        'common.Lesson',
        on_delete=models.CASCADE,
        related_name='student_quizzes',
        null=True
    )
    quizz_type = models.CharField(
        max_length=128,
        choices=QuizzType.choices()
    )
    # start_time = models.DateTimeField()
    quizz_start_time = models.DateTimeField(null=True, blank=True)
    quizz_end_time = models.DateTimeField(null=True, blank=True)

    # end_time = models.DateTimeField()

    class Meta:
        db_table = 'quizz\".\"student_test'

    def __str__(self):
        return f"{self.name_code}"


class StudentQuizzQuestion(
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
        related_name='student_quizz_questions'
    )
    student_quizz = models.ForeignKey(
        'quizzes.StudentQuizz',
        on_delete=models.CASCADE,
        null=True,
        db_index=True,
        related_name='student_quizz_questions'
    )

    class Meta:
        db_table = 'quizz\".\"student_quizz_question'

    def __str__(self):
        return f"{self.student_quizz}"
