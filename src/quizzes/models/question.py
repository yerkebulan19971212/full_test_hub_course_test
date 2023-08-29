from django.db import models
from django.db.models import Prefetch, Count, Q
from django.db.models.functions import Coalesce

from src.common import abstract_models
from src.common.constant import ChoiceType
from src.common.models import QuizzType, CourseTypeQuizz, CourseTypeLesson
from src.quizzes import models as quizzes_models
from src.quizzes.models import StudentQuizz


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

    def get_questions_by_lesson(self, lang: str, lesson: int,
                                course_type: str):
        question_number = 0
        course_types = CourseTypeLesson.objects.filter(
            lesson=lesson,
            course_type__name_code=course_type
        )
        if course_types:
            question_number = course_types.first().questions_number
        return self.filter(
            variant__language=lang,
            lesson_question_level__test_type_lesson__lesson_id=lesson,
            lesson_question_level__question_level__choice=ChoiceType.CHOICE
        )[:question_number]

    def get_questions_with_correct_answer(self):
        queryset = quizzes_models.Answer.objects.filter(correct=True)
        return self.prefetch_related(Prefetch('answers', queryset=queryset))

    def get_question_for_quizz(self, student_quizz_id: int):
        student_quizz = StudentQuizz.objects.get(pk=student_quizz_id)
        answer_queryset = quizzes_models.Answer.objects.all()
        queryset = self.prefetch_related(
            Prefetch('answers', queryset=answer_queryset)
        ).filter(
            lesson_question_level__question_level__choice=ChoiceType.CHOICE,
            variant__language=student_quizz.language,
            lesson_question_level__test_type_lesson__lesson=student_quizz.lesson
        ).annotate(
            question_count=Coalesce(
                Count(
                    'student_quizz_questions',
                    filter=Q(
                        student_quizz_questions__student_quizz__user=student_quizz.user,
                        student_quizz_questions__student_quizz__quizz_type=CourseTypeQuizz.objects.filter(
                            quizz_type__name_code='infinity_quizz').first()
                    ),
                    distinct=True),
                0),
            # filter=
        ).order_by('question_count', '?')
        return queryset

    def get_mat_full_test(self, lang: str):
        return self.select_related(
            'lesson_question_level__test_type_lesson').filter(
            variant__language=lang,
            lesson_question_level__test_type_lesson__lesson__name_code='mathematical_literacy'
        )[:10]

    def get_reading_literacy_full_test(self, lang: str):
        return self.select_related(
            'lesson_question_level__test_type_lesson').filter(
            variant__language=lang,
            lesson_question_level__test_type_lesson__lesson__name_code='reading_literacy'
        )[:10]

    def get_history_full_test(self, lang: str):
        return self.select_related(
            'lesson_question_level__test_type_lesson').filter(
            variant__language=lang,
            lesson_question_level__test_type_lesson__lesson__name_code='history_of_kazakhstan'
        )[:10]

    def get_full_test(self, lang: str, lesson):
        return self.select_related(
            'lesson_question_level__test_type_lesson').filter(
            variant__language=lang,
            lesson_question_level__test_type_lesson__lesson=lesson
        )[:35]


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
