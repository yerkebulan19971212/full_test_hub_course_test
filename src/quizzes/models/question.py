import random
from django.template.defaultfilters import truncatechars
from django.db import models
from django.db.models import Prefetch, Q, Sum
from django.db.models.functions import Coalesce

from src.common import abstract_models
from src.common.constant import ChoiceType, QuestionType
from src.common.models import CourseTypeQuizz
from src.quizzes import models as quizzes_models
from src.quizzes.models import StudentQuizz, QuestionLevel


class CommonQuestionQuerySet(abstract_models.AbstractQuerySet):
    def get_common_question(self, lang, q, packet, lesson, user, quizz_type):
        common_questions = self.filter(
            questions__variant__is_active=True,
            questions__variant__language=lang,
            questions__lesson_question_level__question_level=q,
            questions__variant__variant_packets__packet=packet,
            questions__lesson_question_level__test_type_lesson__lesson__name_code=lesson,
            questions__parent__isnull=True,
        ).annotate(
            user_question_count2=Coalesce(
                Sum(
                    'questions__user_questions_count__quantity',
                    filter=Q(
                        questions__user_questions_count__user=user,
                        questions__user_questions_count__quizz_type=quizz_type
                    )), 0
            )
        ).order_by('user_question_count2')
        common_questions = list(common_questions)
        if len(common_questions) >= 2:
            common_questions = common_questions[:len(common_questions) // 2]
            for i in range(random.randint(1, 5)):
                random.shuffle(common_questions)
        if len(common_questions) == 0:
            return None
        return common_questions[0]


class CommonQuestionManager(models.Manager):
    pass


class CommonQuestion(abstract_models.TimeStampedModel):
    name_code = models.CharField(
        max_length=255,
        # unique=True,
        null=True,
        blank=True
    )
    text = models.TextField(blank=True, null=True)
    file = models.FileField(blank=True, null=True)
    objects = CommonQuestionManager.from_queryset(CommonQuestionQuerySet)()

    class Meta:
        db_table = 'quizz\".\"common_question'

    def __str__(self):
        if self.text:
            return str(self.text)
        return "None"


class QuestionQuerySet(abstract_models.AbstractQuerySet):

    def get_questions_for_flash_card(
            self, student_quizz_id: int, question_number: int, quizz_type):

        student_quizz = StudentQuizz.objects.get(pk=student_quizz_id)
        answer_queryset = quizzes_models.Answer.objects.all()
        queryset = self.prefetch_related(
            Prefetch('answers', queryset=answer_queryset)
        ).filter(
            lesson_question_level__question_level__choice=ChoiceType.CHOICE,
            question_type=QuestionType.DEFAULT,
            common_question__isnull=True,
            variant__language=student_quizz.language,
            variant__variant_packets__packet=student_quizz.packet,
            lesson_question_level__test_type_lesson__lesson=student_quizz.lesson,
        ).annotate(
            question_count=Coalesce(
                Sum(
                    'user_questions_count__quantity',
                    filter=Q(
                        user_questions_count__user=student_quizz.user,
                        user_questions_count__quizz_type=quizz_type
                    )),
                0),
        ).order_by('question_count', '?')
        return queryset[:question_number]

    def get_questions_by_lesson(
            self, lang: str, lesson, user, packet, quizz_type):
        if lesson.name_code == 'reading_literacy':
            return self.get_reading_literacy_full_test_v2(
                lang=lang, packet=packet, user=user, quizz_type=quizz_type)
        elif lesson.name_code == 'history_of_kazakhstan':
            return self.get_history_full_test_v2(
                lang=lang, packet=packet, user=user, quizz_type=quizz_type)
        elif lesson.name_code == 'mathematical_literacy':
            return self.get_mat_full_test_v2(
                lang=lang, packet=packet, user=user, quizz_type=quizz_type)
        else:
            return self.get_full_test_v2(
                lang=lang, lesson=lesson, packet=packet, user=user,
                quizz_type=quizz_type
            )

    def get_questions_with_correct_answer(self):
        queryset = quizzes_models.Answer.objects.filter(correct=True)
        return self.prefetch_related(Prefetch('answers', queryset=queryset))

    def get_question_for_quizz(self, student_quizz_id: int):
        student_quizz = StudentQuizz.objects.get(pk=student_quizz_id)
        answer_queryset = quizzes_models.Answer.objects.all()
        quizz_type = CourseTypeQuizz.objects.filter(
            quizz_type__name_code='infinity_quizz').first()
        queryset = self.prefetch_related(
            Prefetch('answers', queryset=answer_queryset)
        ).filter(
            lesson_question_level__question_level__choice=ChoiceType.CHOICE,
            question_type=QuestionType.DEFAULT,
            common_question__isnull=True,
            variant__language=student_quizz.language,
            variant__variant_packets__packet=student_quizz.packet,
            lesson_question_level__test_type_lesson__lesson=student_quizz.lesson,
        ).annotate(
            question_count=Coalesce(
                Sum(
                    'user_questions_count__quantity',
                    filter=Q(
                        user_questions_count__user=student_quizz.user,
                        user_questions_count__quizz_type=quizz_type
                    )),
                0),
        ).order_by('question_count', '?')
        return queryset

    def get_mat_full_test_v2(self, lang: str, packet, user, quizz_type):
        questions = list(self.select_related(
            'lesson_question_level__test_type_lesson',
        ).filter(
            variant__language=lang,
            variant__is_active=True,
            variant__variant_packets__packet=packet,
            lesson_question_level__test_type_lesson__lesson__name_code='mathematical_literacy'
        ).annotate(
            user_question_count=Coalesce(
                Sum(
                    'user_questions_count__quantity',
                    filter=Q(
                        user_questions_count__user=user,
                        user_questions_count__quizz_type=quizz_type
                    )),
                0)
        ).order_by('user_question_count'))
        questions_count = len(questions)
        if questions_count >= 20:
            questions = questions[:questions_count // 2]
        for i in range(random.randint(1, 5)):
            random.shuffle(questions)
        return questions[:10]

    def get_reading_literacy_full_test_v2(self, lang: str, packet, user,
                                          quizz_type):
        questions_list = []
        for q in QuestionLevel.objects.order_by('id')[:3]:
            common_question = CommonQuestion.objects.get_common_question(
                lang=lang, q=q,
                packet=packet,
                lesson='reading_literacy',
                user=user,
                quizz_type=quizz_type
            )
            question_index = 2
            if q.name_code == 'B':
                question_index = 3
            elif q.name_code == 'C':
                question_index = 5
            questions = list(
                self.select_related(
                    'lesson_question_level__test_type_lesson',
                ).filter(
                    common_question=common_question
                ))[:question_index]
            random.shuffle(questions)
            questions_list += questions
        return questions_list

    def get_history_full_test_v2(self, lang: str, packet, user, quizz_type):
        questions_list = []
        queryset = self.select_related(
            'lesson_question_level__test_type_lesson',
        )
        for q in QuestionLevel.objects.all().order_by('id')[:4]:
            if q.name_code == 'C' or q.name_code == 'D':
                common_question = CommonQuestion.objects.get_common_question(
                    lang=lang, q=q,
                    packet=packet,
                    lesson='history_of_kazakhstan',
                    user=user, quizz_type=quizz_type
                )
                questions = queryset.filter(common_question=common_question)
                questions_list += [q for q in questions[:5]]
                continue
            questions = queryset.filter(
                variant__language=lang,
                variant__is_active=True,
                lesson_question_level__question_level=q,
                variant__variant_packets__packet=packet,
                lesson_question_level__test_type_lesson__lesson__name_code='history_of_kazakhstan'
            ).annotate(
                user_question_count=Coalesce(
                    Sum(
                        'user_questions_count__quantity',
                        filter=Q(
                            user_questions_count__user=user,
                            user_questions_count__quizz_type=quizz_type
                        )),
                    0)
            ).order_by('user_question_count')
            questions = list(questions)
            if len(questions) >= 10:
                questions = questions[:len(questions) // 2]
                for i in range(random.randint(1, 5)):
                    random.shuffle(questions)
            else:
                random.shuffle(questions)
            if q.name_code == 'C' or q.name_code == 'D':
                common_question = CommonQuestion.objects.get_common_question(
                    lang=lang, q=q,
                    packet=packet,
                    lesson='history_of_kazakhstan',
                    user=user,
                    quizz_type=quizz_type
                )
                questions = list(
                    queryset.filter(common_question=common_question))
                random.shuffle(questions)
            questions_list += questions[:5]
        return questions_list

    def get_full_test_v2(self, lang: str, lesson, packet, user, quizz_type):
        questions_list = []
        queryset = self.select_related(
            'lesson_question_level__test_type_lesson',
        )
        for q in QuestionLevel.objects.all().order_by('id'):
            if q.name_code == 'F':
                common_question = CommonQuestion.objects.get_common_question(
                    lang=lang, q=q,
                    packet=packet,
                    lesson=lesson.name_code,
                    user=user, quizz_type=quizz_type
                )
                if common_question:
                    questions = list(
                        queryset.filter(common_question=common_question))
                    random.shuffle(questions)
                    questions_list += questions
                    continue
            questions = list(queryset.filter(
                variant__is_active=True,
                variant__language=lang,
                lesson_question_level__question_level=q,
                variant__variant_packets__packet=packet,
                lesson_question_level__test_type_lesson__lesson=lesson,
                parent__isnull=True
            ).annotate(
                user_question_count=Coalesce(
                    Sum(
                        'user_questions_count__quantity',
                        filter=Q(
                            user_questions_count__user=user,
                            user_questions_count__quizz_type=quizz_type
                        )),
                    0)
            ).order_by('user_question_count'))
            if len(questions) >= 10:
                questions = questions[:len(questions) // 2]
                for i in range(random.randint(1, 5)):
                    random.shuffle(questions)
            else:
                random.shuffle(questions)
            questions_list += questions[:5]
        return questions_list


class QuestionManager(models.Manager):
    pass


class Question(
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel
):
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True,
        related_name="sub_questions"
    )
    question_type = models.CharField(
        max_length=11,
        choices=QuestionType.choices(),
        default=QuestionType.DEFAULT,
        db_index=True,
    )
    common_question = models.ForeignKey(
        'quizzes.CommonQuestion',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        db_index=True,
        related_name='questions'
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
        db_index=True,
        related_name='questions'
    )
    answer_question = models.TextField(null=True, blank=True)
    answer_url = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    objects = QuestionManager.from_queryset(QuestionQuerySet)()

    class Meta:
        db_table = 'quizz\".\"question'

    def __str__(self):
        return f'{self.question}'

    @property
    def short_question(self):
        return truncatechars(self.question, 100)

    @property
    def level_name(self):
        return self.lesson_question_level.question_level.name_code


class UserQuestionCount(models.Model):
    question = models.ForeignKey(
        'quizzes.Question',
        on_delete=models.CASCADE,
        null=True,
        db_index=True,
        related_name='user_questions_count'
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        null=True,
        db_index=True,
        related_name='user_questions_count'
    )
    quizz_type = models.ForeignKey(
        'common.CourseTypeQuizz',
        on_delete=models.CASCADE,
        related_name='user_questions_count',
        null=True,
        db_index=True
    )
    quantity = models.IntegerField(default=0)

    class Meta:
        db_table = 'quizz\".\"user_questions_count'

    def __str__(self):
        return f"{self.user}"
