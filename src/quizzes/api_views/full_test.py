from datetime import datetime, timedelta

from django.db import transaction
from django.db.models import (Sum, Avg, Count, Q, Prefetch, Exists, OuterRef, Max,
                              Case, When, IntegerField, F, Value, CharField,
                              BooleanField, Subquery)
from django.db.models.functions import Concat, Coalesce

from django.utils import timezone
from rest_framework import generics, status
from rest_framework import permissions
from rest_framework import views
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from config.celery import finish_test
from src.common import constant
from src.common.constant import ChoiceType, QuizzStatus
from src.common.exception import PassedTestError
from src.common.models import Lesson, CourseTypeLesson, RatingTest, \
    CourseTypeQuizz
from src.common.paginations import SimplePagination
from src.common.utils import get_multi_score
from src.quizzes.filters import StudentQuizFileFilterSerializer
from src.quizzes.models import Question, Answer, StudentScore, StudentAnswer, \
    TestFullScore
from src.quizzes import serializers
from src.quizzes import filters
from src.quizzes.models.student_quizz import StudentQuizzQuestion, \
    StudentQuizz, StudentQuizzFile
from src.quizzes.serializers import FullQuizQuestionQuerySerializer
from src.services.services import get_result_lesson
from src.services.utils import finish_full_test, get_result_st


class MyTest(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = StudentQuizz.objects.all()
    serializer_class = serializers.MyTestSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.MyTestFilter

    def get_queryset(self):
        current_time = timezone.now()
        tests = super().get_queryset().filter(
            user=self.request.user,
            status__in=[QuizzStatus.CONTINUE, QuizzStatus.NOT_PASSED],
            quizz_start_time__lt=current_time - F('quizz_duration')
        )
        for test in tests:
            finish_test.delay(test.id)
        return super().get_queryset().filter(
            user=self.request.user
        ).annotate(
            quantity_question=Coalesce(Count('student_quizz_questions'), 0),
        ).order_by('-created')


my_test_view = MyTest.as_view()


class NewTestView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.NewTestSerializer


new_test_view = NewTestView.as_view()


class GetFilesView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = StudentQuizzFile.objects.all()
    serializer_class = serializers.StudentQuizzFileSerializer

    @swagger_auto_schema(query_serializer=StudentQuizFileFilterSerializer)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


get_files_view = GetFilesView.as_view()


class NewFullTest(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.FullQuizzSerializer

    @swagger_auto_schema(tags=["full-test"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


new_full_test_view = NewFullTest.as_view()


class StudentQuizzInformationView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.StudentQuizzInformationSerializer
    queryset = StudentQuizz.objects.select_related().all()
    lookup_field = 'pk'

    @swagger_auto_schema(tags=["full-test"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


full_quizz_view = StudentQuizzInformationView.as_view()


class FullQuizLessonListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.FullQuizLessonListSerializer
    queryset = Lesson.objects.all()

    @swagger_auto_schema(tags=["full-test"])
    def get(self, request, *args, **kwargs):
        student_id = self.kwargs.get('student_quizz')
        student_test = get_object_or_404(StudentQuizz, pk=student_id)

        if (student_test.status != "NOT_PASSED" and
                student_test.status != "CONTINUE"):
            return Response({"detail": "Вы уже прошли этот тест"},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            student_test.status = "CONTINUE"
            student_test.save()

        if not student_test.quizz_start_time:
            student_test.quizz_start_time = datetime.now()
            student_test.save()
            # difference_duration = timedelta(seconds=0)
        current_time = timezone.now()
        duration = (
                           student_test.quizz_start_time + student_test.quizz_duration) - current_time
        if duration.total_seconds() <= 0:
            student_test.quizz_duration = timedelta(seconds=0)
            student_test.save()
            return Response({"detail": "Вы уже прошли этот тест"},
                            status=status.HTTP_400_BAD_REQUEST)
        student_test.save()
        data = self.list(request, *args, **kwargs).data

        return Response({
            "lessons": data,
            "duration": {
                "hour": duration.seconds // 3600,
                "minute": (duration.seconds % 3600) // 60,
                "seconds": duration.seconds % 60,
            }
        }, status=status.HTTP_200_OK)

    def get_queryset(self):
        student_test_id = self.kwargs.get('student_quizz')
        student_quizz = get_object_or_404(
            StudentQuizz.objects.select_related(
                'lesson_pair',
                'lesson_pair__lesson_2',
                'lesson_pair__lesson_1',
            ), pk=student_test_id)

        queryset = self.queryset
        main_lessons = queryset.filter(
            course_type_lessons__main=True,
        ).order_by('course_type_lessons__main', 'id')
        if not student_quizz.lesson_pair:
            main_lessons = main_lessons.exclude(
                name_code="mathematical_literacy")
            # lesson_1_name_code = student_quizz.lesson_pair.lesson_1.name_code
            # if lesson_1_name_code == "creative_exam":
            #     main_lessons = main_lessons.exclude(
            #         name_code="mathematical_literacy")
        elif student_quizz.lesson_pair:
            lesson_1_name_code = student_quizz.lesson_pair.lesson_1.name_code
            if lesson_1_name_code == "creative_exam":
                main_lessons = main_lessons.exclude(
                    name_code="mathematical_literacy")
            else:
                other_lessons = queryset.filter(
                    course_type_lessons__course_type__name_code="ent",
                    id__in=[student_quizz.lesson_pair.lesson_1_id,
                            student_quizz.lesson_pair.lesson_2_id])
                main_lessons = main_lessons | other_lessons

        return main_lessons.order_by('-course_type_lessons__main', 'id')


full_quizz_lesson_view = FullQuizLessonListView.as_view()


class FullQuizQuestionListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.FullQuizQuestionSerializer
    queryset = Question.objects.select_related(
        'common_question',
        'lesson_question_level',
        'lesson_question_level__question_level'
    ).prefetch_related(
        'answers',
    ).filter(parent__isnull=True)

    @swagger_auto_schema(tags=["full-test"],
                         query_serializer=FullQuizQuestionQuerySerializer)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        student_quizz_id = self.request.query_params.get('student_quizz_id')
        lesson_id = self.request.query_params.get('lesson_id')

        answer = StudentAnswer.objects.filter(
            student_quizz_id=student_quizz_id,
            status=True
        )
        sub_questions = Question.objects.prefetch_related(
            "answers",
            Prefetch('student_answers', queryset=answer),
        )
        return super().get_queryset().prefetch_related(
            Prefetch('student_answers', queryset=answer),
            Prefetch('sub_questions', queryset=sub_questions),
        ).filter(
            student_quizz_questions__lesson_id=lesson_id,
            student_quizz_questions__student_quizz_id=student_quizz_id,
        ).order_by('student_quizz_questions__order')


full_quizz_question_view = FullQuizQuestionListView.as_view()


class PassStudentAnswerView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.StudentAnswersSerializer

    @swagger_auto_schema(tags=["full-test"])
    def post(self, request, format=None):
        data = self.request.data
        question_id = data.get('question')
        student_quizz_id = data.get('student_quizz')
        answers = data.get('answers')
        if answers:
            try:
                with transaction.atomic():
                    score = 0
                    question = Question.objects.select_related(
                        'lesson_question_level__question_level',
                        'lesson_question_level__test_type_lesson__lesson',
                    ).get(pk=question_id)
                    lesson = question.lesson_question_level.test_type_lesson.lesson
                    correct_answers = question.answers.filter(correct=True)
                    StudentAnswer.objects.filter(
                        student_quizz_id=student_quizz_id,
                        question=question,
                    ).update(status=False)
                    StudentAnswer.objects.bulk_create([
                        StudentAnswer(
                            student_quizz_id=student_quizz_id,
                            question=question,
                            lesson=lesson,
                            answer_id=a
                        ) for a in answers
                    ])
                    question_choice = question.lesson_question_level.question_level.choice
                    if question_choice == ChoiceType.CHOICE:
                        if correct_answers[0].id == answers[0]:
                            score += 1
                    else:
                        user_answers = Answer.objects.filter(id__in=answers)
                        len_student_answers = user_answers.count()
                        if len_student_answers > 4:
                            user_answers = list(set(user_answers))
                            correct_answers = list(
                                set([ans for ans in correct_answers]))
                            score += get_multi_score(user_answers,
                                                     correct_answers)
                    StudentScore.objects.filter(
                        student_quizz_id=student_quizz_id,
                        question=question
                    ).update(status=False)
                    StudentScore.objects.get_or_create(
                        student_quizz_id=student_quizz_id,
                        question=question,
                        lesson=lesson,
                        score=score,
                        status=True
                    )
            except Exception as e:
                print(e)
                return Response({"detail": str(e)},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Success"})


pass_answer_view = PassStudentAnswerView.as_view()


class EntFinishView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(tags=["full-test"])
    def post(self, request, student_quizz):
        student_quizz = get_object_or_404(StudentQuizz, pk=student_quizz)
        if student_quizz.status in ["PASSED"]:
            raise PassedTestError()
        finish_full_test(student_quizz.id)
        return Response({"detail": "success"}, status=status.HTTP_201_CREATED)


full_test_finish_view = EntFinishView.as_view()


class GetTestFullScoreResultListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.TestFullScoreSerializer
    queryset = TestFullScore.objects.select_related('lesson').all()

    @swagger_auto_schema(tags=["full-test"])
    def get(self, request, *args, **kwargs):
        student_quizz_id = self.kwargs.get('pk')
        data = super().get(request, *args, **kwargs).data
        data = get_result_lesson(student_quizz_id, data)
        return Response(data)

    def get_queryset(self):
        student_quizz_id = self.kwargs.get('pk')
        return super().get_queryset().filter(student_quizz_id=student_quizz_id)


get_full_test_full_score_result_view = GetTestFullScoreResultListView.as_view()


class StudentQuizFinishInfoListView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.ResultScoreSerializer
    queryset = Question.objects.all().annotate(
        sum_score=Sum('question_score__score',
                      filter=Q(question_score__status=True))
    ).order_by('student_quizz_questions__order')

    @swagger_auto_schema(tags=["full-test"])
    def get(self, request, *args, **kwargs):
        student_quizz_id = self.kwargs.get('pk')
        data = get_result_st(student_quizz_id=student_quizz_id)
        return Response(data)


st_result_view = StudentQuizFinishInfoListView.as_view()


class ResultQuestionView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.QuestionResultSerializer
    queryset = Question.objects.prefetch_related(
        'answers__answer_sign'
    ).all()
    lookup_field = 'pk'

    @swagger_auto_schema(tags=["full-test"])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


get_result_question = ResultQuestionView.as_view()


class ResultRatingView(generics.ListAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.StudentQuizzRatingSerializer
    queryset = TestFullScore.objects.filter(
        student_quizz__bought_packet__rating_test__isnull=False
    )
    pagination_class = SimplePagination

    @swagger_auto_schema(query_serializer=filters.RatingFilterSerializer)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        q = self.request.query_params.get("q")
        school_id = self.request.query_params.get("school_id")
        lesson_pair_id = self.request.query_params.get("lesson_pair_id")
        rating_period_id = self.request.query_params.get("rating_period_id",
                                                         None)
        queryset = super().get_queryset()
        if q:
            queryset = queryset.filter(
                Q(student_quizz__user__first_name__icontains=q) |
                Q(student_quizz__user__last_name__icontains=q) |
                Q(student_quizz__user__school__name_en__icontains=q) |
                Q(student_quizz__user__school__name_ru__icontains=q) |
                Q(student_quizz__user__school__name_kz__icontains=q)
            )
        if school_id:
            queryset = queryset.filter(
                student_quizz__user__school_id=school_id
            )
        if lesson_pair_id:
            queryset = queryset.filter(
                student_quizz__lesson_pair_id=lesson_pair_id
            )
        if rating_period_id is None:
            rating_period = RatingTest.objects.all().order_by('id').last()
            rating_period_id = rating_period.id
        if rating_period_id:
            queryset = queryset.filter(
                student_quizz__bought_packet__rating_test_id=rating_period_id)
        queryset = queryset.values(
            'student_quizz',
            'student_quizz__user__city__name_ru',
            'student_quizz__user__first_name',
            'student_quizz__user__last_name',
            'student_quizz__lesson_pair__lesson_1',
            'student_quizz__lesson_pair__lesson_2',
        ).annotate(
            total_count=Coalesce(Sum('score'), 0),
            is_current=
            Case(When(student_quizz__user_id=user.id, then=True),
                 default=False,
                 output_field=BooleanField()),
            math=Max(
                Case(When(lesson__id=15, then='score'), default=None,
                     output_field=IntegerField())),
            literacy=Max(
                Case(When(lesson__id=6, then='score'), default=None,
                     output_field=IntegerField())),
            history=Max(
                Case(When(lesson__id=7, then='score'), default=None,
                     output_field=IntegerField())),
            lesson_1_ru=Concat(
                F('student_quizz__lesson_pair__lesson_1__name_ru'),
                Value(' - '),
                Max(Case(When(lesson__id=F(
                    'student_quizz__lesson_pair__lesson_1_id'),
                    then='score'), default=None,
                    output_field=CharField()))),
            lesson_1_kz=Concat(
                F('student_quizz__lesson_pair__lesson_1__name_kz'),
                Value(' - '),
                Max(Case(When(lesson__id=F(
                    'student_quizz__lesson_pair__lesson_1_id'),
                    then='score'), default=None,
                    output_field=CharField()))),
            lesson_1_en=Concat(
                F('student_quizz__lesson_pair__lesson_1__name_en'),
                Value(' - '),
                Max(Case(When(lesson__id=F(
                    'student_quizz__lesson_pair__lesson_1_id'),
                    then='score'), default=None,
                    output_field=CharField()))),
            lesson_2_ru=Concat(
                F('student_quizz__lesson_pair__lesson_2__name_ru'),
                Value(' - '),
                Max(Case(When(lesson__id=F(
                    'student_quizz__lesson_pair__lesson_2_id'),
                    then='score'), default=None,
                    output_field=CharField()))),
            lesson_2_kz=Concat(
                F('student_quizz__lesson_pair__lesson_2__name_kz'),
                Value(' - '),
                Max(Case(When(lesson__id=F(
                    'student_quizz__lesson_pair__lesson_2_id'),
                    then='score'), default=None,
                    output_field=CharField()))),
            lesson_2_en=Concat(
                F('student_quizz__lesson_pair__lesson_2__name_en'),
                Value(' - '),
                Max(Case(When(lesson__id=F(
                    'student_quizz__lesson_pair__lesson_2_id'),
                    then='score'), default=None,
                    output_field=CharField()))),
        ).order_by('-total_count')

        return queryset


result_rating = ResultRatingView.as_view()


class MyProgressView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = TestFullScore.objects.all().filter()
    serializer_class = serializers.MyProgressSerializer

    def get_queryset(self):
        return super().get_queryset().filter(
            student_quizz__user=self.request.user,
            student_quizz__quizz_type__quizz_type__name_code='full_test',
            student_quizz__status=QuizzStatus.PASSED,
        ).values(
            'student_quizz',
            'student_quizz__created'
        ).annotate(
            score_sum=Sum('score')
        ).order_by('-student_quizz')[:10]

    def get(self, request, *args, **kwargs):
        average_score = 0
        min_score = 0
        max_score = 0
        data = self.list(request, *args, **kwargs).data
        score_values = [d['score_sum'] for d in data]
        if score_values:
            average_score = sum(score_values) / len(score_values)
            min_score = min(score_values)
            max_score = max(score_values)
        return Response({
            "tests": data,
            "average_score": average_score,
            "min_score": min_score,
            "max_score": max_score,
        })


my_progress_view = MyProgressView.as_view()


class MyLessonProgressView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = TestFullScore.objects.all()
    serializer_class = serializers.MyLessonProgressSerializer

    def get_queryset(self):
        return super().get_queryset().filter(
            student_quizz__user=self.request.user,
            student_quizz__quizz_type__quizz_type__name_code='full_test',
            student_quizz__status=QuizzStatus.PASSED,
        ).values(
            'lesson__course_type_lessons__main',
            'lesson__name_kz',
            'lesson__name_ru',
            'lesson__name_en',
            'lesson__icon',
        ).annotate(
            score_sum=Avg('score')
        ).filter(score_sum__gte=1).distinct()[:10]

    def get(self, request, *args, **kwargs):
        data = self.list(request, *args, **kwargs).data
        main = []
        not_main = []
        for d in data:
            if d.get('main'):
                main.append(d)
            else:
                not_main.append(d)
        return Response({
            "main": main,
            "not_main": not_main,
        })


my_lesson_progress_view = MyLessonProgressView.as_view()
