from django.db import models
from src.common import abstract_models
from src.common.constant import QuizzType, QuizzStatus, TestLang


class StudentQuizz(
    abstract_models.UUID,
    abstract_models.TimeStampedModel
):
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_index=True
    )
    user = models.ForeignKey(
        'accounts.User',
        related_name='student_quizzes',
        on_delete=models.CASCADE,
        db_index=True
    )
    course_type = models.ForeignKey(
        'common.CourseType',
        on_delete=models.CASCADE,
        db_index=True,
        related_name='student_quizzes'
    )
    packet = models.ForeignKey(
        'common.Packet',
        on_delete=models.CASCADE,
        db_index=True,
        related_name='student_quizzes',
        null=True
    )
    bought_packet = models.ForeignKey(
        'common.BoughtPacket',
        on_delete=models.CASCADE,
        db_index=True,
        related_name='student_quizzes',
        null=True
    )
    status = models.CharField(
        max_length=12,
        choices=QuizzStatus.choices(),
        default=QuizzStatus.NOT_PASSED,
        db_index=True
    )
    lesson = models.ForeignKey(
        'common.Lesson',
        on_delete=models.CASCADE,
        related_name='student_quizzes',
        null=True,
        db_index=True
    )
    lesson_pair = models.ForeignKey(
        'common.LessonPair',
        on_delete=models.CASCADE,
        related_name='student_quizzes',
        null=True,
        db_index=True
    )
    quizz_type = models.ForeignKey(
        'common.CourseTypeQuizz',
        on_delete=models.CASCADE,
        related_name='student_quizzes',
        null=True,
        db_index=True
    )
    language = models.CharField(
        max_length=64,
        choices=TestLang.choices(),
        default=TestLang.KAZAKH,
        db_index=True
    )
    quizz_duration = models.DurationField(default="0", null=True, blank=True)
    quizz_start_time = models.DateTimeField(null=True, blank=True)
    quizz_end_time = models.DateTimeField(null=True, blank=True)

    # end_time = models.DateTimeField()

    class Meta:
        db_table = 'quizz\".\"student_test'

    # def __str__(self):
    #     return f"{self.name_code}"


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
    lesson = models.ForeignKey(
        'common.Lesson',
        on_delete=models.CASCADE,
        null=True,
        db_index=True,
        related_name='student_quizz_questions'
    )
    flash_card_status = models.BooleanField(null=True)

    class Meta:
        db_table = 'quizz\".\"student_quizz_question'

    def __str__(self):
        return f"{self.student_quizz}"


class StudentQuizzFile(
    abstract_models.UUID,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel
):
    icon = models.FileField(upload_to='student-quizz/icon')
    file = models.FileField(upload_to='student-quizz/file')
    file_name = models.CharField(max_length=1024, null=True)
    course_type = models.ForeignKey(
        'common.QuizzType',
        on_delete=models.CASCADE,
        null=True,
        db_index=True,
        related_name='course_type_files',
    )
