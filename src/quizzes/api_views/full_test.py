from datetime import datetime, timedelta

from django.db import transaction
from django.db.models import Sum, Count, Q, Prefetch, Exists, OuterRef
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.dateparse import parse_duration
from rest_framework import generics, status
from rest_framework import permissions
from rest_framework import views
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from src.common.constant import ChoiceType
from src.common.models import Lesson, CourseTypeLesson
from src.common.utils import get_multi_score
from src.quizzes.filters import StudentQuizFileFilterSerializer
from src.quizzes.models import Question, Answer, StudentScore, StudentAnswer, \
    TestFullScore
from src.quizzes import serializers
from src.quizzes import filters
from src.quizzes.models.student_quizz import StudentQuizzQuestion, \
    StudentQuizz, StudentQuizzFile
from src.quizzes.serializers import FullQuizQuestionQuerySerializer


class MyTest(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = StudentQuizz.objects.all()
    serializer_class = serializers.MyTestSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.MyTestFilter

    def get_queryset(self):
        return super().get_queryset().filter(
            user=self.request.user
        ).annotate(
            quantity_question=Coalesce(Count('student_quizz_questions'), 0),
        ).order_by('-created')


my_test_view = MyTest.as_view()


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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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
    # # def get_queryset(self):
    # #     pk = self.kwargs.get('pk')
    # #     user = self.request.user
    # #     test_type = self.kwargs.get('test_type')
    # #     queryset = self.queryset.filter(
    # #         pk=pk,
    # #         user=user,
    #         variant__variant_lessons__lesson__test_type_lessons__type__name=test_type
    #     # )
    #     student_test = queryset.first()
    #     test_start_time = student_test.test_start_time
    #     duration = student_test.variant.duration
    #     difference_duration = datetime.now() - localtime(
    #         test_start_time).replace(tzinfo=None)
    #     if duration < difference_duration:
    #         finish_ent(student_test)
    #     # return queryset.all()


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
            # difference_duration = timedelta(seconds=0)
        else:
            test_start_time = student_test.quizz_start_time
        duration = student_test.quizz_type.quizz_type.quizz_duration
        duration_dif = timezone.now() - student_test.quizz_start_time
        if duration.total_seconds() <= 0:
            student_test.quizz_duration = timedelta(seconds=0)
            student_test.status = "PASSED"
            student_test.save()
            return Response({"detail": "Вы уже прошли этот тест"},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            student_test.quizz_duration = duration
        student_test.save()
        data = self.list(request, *args, **kwargs).data
        duration = student_test.quizz_duration
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
            course_type_lessons__course_type__name_code='ent',
            course_type_lessons__main=True,
        ).order_by('course_type_lessons__main', 'id')
        if student_quizz.lesson_pair.lesson_1.name_ru == "Творческий экзамен":
            main_lessons = main_lessons.exclude(
                name_ru="Математическая грамотность")
        if student_quizz.lesson_pair and not student_quizz.lesson_pair.lesson_1.name_ru == "Творческий экзамен":
            other_lessons = queryset.filter(
                course_type_lessons__course_type__name_code="ent",
                id__in=[student_quizz.lesson_pair.lesson_1_id,
                        student_quizz.lesson_pair.lesson_2_id])
            main_lessons = main_lessons | other_lessons
        main_lessons = main_lessons.annotate(
            sum_of_questions=Count('student_quizz_questions',
                                   filter=Q(
                                       student_quizz_questions__student_quizz=student_quizz))
        )

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
        'student_quizz_questions',
    ).all().distinct()

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
        return super().get_queryset().prefetch_related(
            Prefetch('student_answers', queryset=answer)
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
                        'lesson_question_level__question_level'
                    ).get(pk=question_id)
                    correct_answers = question.answers.filter(correct=True)
                    StudentAnswer.objects.filter(
                        student_quizz_id=student_quizz_id,
                        question=question,
                    ).update(status=False)
                    StudentAnswer.objects.bulk_create([
                        StudentAnswer(
                            student_quizz_id=student_quizz_id,
                            question=question,
                            answer_id=a
                        ) for a in answers
                    ])
                    question_choice = question.lesson_question_level.question_level.choice
                    if question_choice == ChoiceType.CHOICE:
                        if correct_answers[0].id == answers[0]:
                            score += 1
                    else:
                        len_correct_answers = correct_answers.count()
                        user_answers = Answer.objects.filter(id__in=answers)
                        len_student_answers = user_answers.count()
                        if len_correct_answers >= len_student_answers:
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
        student_quizz.status = "PASSED"
        student_quizz.quizz_end_time = datetime.now()
        student_quizz.save()
        if student_quizz.lesson_pair:
            test_type_lessons = CourseTypeLesson.objects.filter(
                main=True, course_type__name_code='ent'
            )
            lessons = [test_type_lesson.lesson for test_type_lesson in
                       test_type_lessons]
            lesson_pair = student_quizz.lesson_pair
            lessons.append(lesson_pair.lesson_1)
            lessons.append(lesson_pair.lesson_2)
        else:
            lessons = [student_quizz.lesson]
        index = 0
        test_full_score = []
        for lesson in lessons:
            index += 1
            question_score = StudentScore.objects.filter(
                question__student_quizz_questions__lesson=lesson,
                student_quizz=student_quizz,
                status=True
            ).distinct().aggregate(sum_score=Coalesce(Sum('score'), 0))
            quantity_question = StudentQuizzQuestion.objects.filter(
                student_quizz=student_quizz,
                lesson=lesson
            ).count()
            question_full_score = StudentQuizzQuestion.objects.filter(
                student_quizz=student_quizz,
                lesson=lesson
            ).distinct().aggregate(
                sum_score=Coalesce(
                    Sum('question__lesson_question_level__question_level__point'),
                    0)
            ).get("sum_score")
            score = question_score.get('sum_score', 0)
            test_full_score.append(
                TestFullScore(
                    student_quizz=student_quizz,
                    lesson=lesson,
                    score=score,
                    unattem=quantity_question - score,
                    number_of_score=question_full_score,
                    number_of_question=quantity_question,
                    accuracy=100 * score / question_full_score
                ))
        TestFullScore.objects.bulk_create(test_full_score)
        return Response({"detail": "success"}, status=status.HTTP_201_CREATED)


full_test_finish_view = EntFinishView.as_view()


class GetTestFullScoreResultListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.TestFullScoreSerializer
    queryset = TestFullScore.objects.all()

    @swagger_auto_schema(tags=["full-test"])
    def get(self, request, *args, **kwargs):
        student_quizz_id = self.kwargs.get('pk')
        data = super().get(request, *args, **kwargs).data
        for d in data:
            questions = Question.objects.filter(
                student_quizz_questions__student_quizz_id=student_quizz_id,
                student_quizz_questions__lesson_id=d.get('lesson_id'),
            ).annotate(
                answered_correct=Exists(
                    StudentAnswer.objects.filter(
                        student_quizz_id=student_quizz_id,
                        question_id=OuterRef('pk'),
                        answer__correct=True,
                        status=True,
                    )),
                answered=Exists(
                    StudentAnswer.objects.filter(
                        student_quizz_id=student_quizz_id,
                        question_id=OuterRef('pk'),
                        status=True,
                    ))
            ).order_by('student_quizz_questions__order')
            d['questions'] = []
            for q in questions:
                answered = 'NOT_ANSWERED'
                if q.answered_correct and q.answered:
                    answered = 'CORRECT'
                elif q.answered_correct is False and q.answered:
                    answered = 'WRONG'
                d['questions'].append({
                    "question_id": q.id,
                    "correct_answered": answered,
                })
        return Response(data)

    def get_queryset(self):
        student_quizz_id = self.kwargs.get('pk')
        return super().get_queryset().filter(student_quizz_id=student_quizz_id)


get_full_test_full_score_result_view = GetTestFullScoreResultListView.as_view()


# class GetResultListView(generics.ListAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = serializers.ResultScoreSerializer
#     queryset = Question.objects.all().annotate(
#         sum_score=Sum('question_score__score',
#                       filter=Q(question_score__status=True))
#     ).order_by('student_quizz_questions__order')
#     filter_backends = [DjangoFilterBackend]
#     filterset_class = filters.FullQuizzQuestionFilter
#
#     @swagger_auto_schema(tags=["full-test"])
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#
# get_full_test_result_view = GetResultListView.as_view()


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
        student_quizz = StudentQuizz.objects.get(pk=student_quizz_id)
        total_score = TestFullScore.objects.filter(
            student_quizz_id=student_quizz_id
        ).aggregate(total_score=Coalesce(Sum('score'), 0)).get("total_score")
        total_bal = 140
        answered_questions = StudentAnswer.objects.filter(
            student_quizz=student_quizz_id,
            status=True
        ).aggregate(
            answered_questions=Coalesce(Count('question_id', distinct=True), 0)
        ).get("answered_questions")
        quantity_correct_question = StudentAnswer.objects.filter(
            student_quizz=student_quizz_id,
            status=True,
            answer__correct=True
        ).aggregate(
            answered_questions=Coalesce(Count('question_id', distinct=True), 0)
        ).get("answered_questions")
        quantity_question = StudentQuizzQuestion.objects.filter(
            student_quizz=student_quizz
        ).count()
        if answered_questions > 0:
            correct_question_percent = 100 * quantity_correct_question / answered_questions
        else:
            correct_question_percent = 0
        return Response({
            "total_user_score": total_score,
            "total_score": total_bal,
            "start_time": student_quizz.quizz_start_time,
            "end_time": student_quizz.quizz_end_time,
            "duration": student_quizz.quizz_end_time - student_quizz.quizz_start_time,
            "quantity_question": quantity_question,
            "quantity_answered_questions": answered_questions,
            "quantity_correct_question": quantity_correct_question,
            "quantity_wrong_question": answered_questions - quantity_correct_question,
            "correct_question_percent": correct_question_percent,
        })


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
