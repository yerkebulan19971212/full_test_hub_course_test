from datetime import datetime

from django.db import transaction
from django.db.models import Sum, Count, Q, Prefetch, Exists, OuterRef
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.dateparse import parse_duration
from rest_framework import generics, status
from rest_framework import permissions
from rest_framework import views
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from src.common.constant import ChoiceType, QuestionType
from src.common.exception import PassedTestError
from src.common.models import Lesson, CourseTypeLesson
from src.common.utils import get_multi_score
from src.quizzes.models import (Question, Answer, StudentScore, StudentAnswer,
                                TestFullScore, StudentQuizzQuestion, StudentQuizz)
from src.quizzes import serializers
from src.quizzes.serializers import FullQuizQuestionQuerySerializer
from src.services.utils import finish_full_test


class NewByLessonQuiz(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.ByLessonQuizzSerializer

    @swagger_auto_schema(tags=["by-lesson"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


new_by_lesson_quizz_view = NewByLessonQuiz.as_view()


class StudentQuizzInformationView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.StudentQuizzInformationSerializer
    queryset = StudentQuizz.objects.select_related().all()
    lookup_field = 'pk'

    @swagger_auto_schema(tags=["by-lesson"])
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


by_lesson_quizz_view = StudentQuizzInformationView.as_view()


class ByLessonQuizLessonListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.FullQuizLessonListSerializer
    queryset = Lesson.objects.all()

    @swagger_auto_schema(tags=["by-lesson"])
    def get(self, request, *args, **kwargs):
        student_id = self.kwargs.get('student_quizz')
        student_test = get_object_or_404(StudentQuizz, pk=student_id)

        if (student_test.status != "NOT_PASSED" and
                student_test.status != "CONTINUE"):
            return Response({"detail": "Вы уже прошли этот тест"},
                            status=status.HTTP_400_BAD_REQUEST)
            # elif datetime.now() > localtime(student_test.end_time).replace(
            #         tzinfo=None):
            # return Response({"detail": "Тест тапсыратын уакыт отип кетти"},
            #                 status=status.HTTP_400_BAD_REQUEST)
        else:
            student_test.status = "CONTINUE"
            student_test.save()
        duration_time = {
            "hour": 0,
            "minute": 0,
            "seconds": 0
        }
        if not student_test.quizz_start_time:
            student_test.quizz_start_time = datetime.now()
            student_test.save()
            # difference_duration = timedelta(seconds=0)
        else:
            test_start_time = student_test.quizz_start_time
            # difference_duration = datetime.now() - localtime(
            #     test_start_time).replace(tzinfo=None)
        duration = student_test.quizz_type.quizz_type.quizz_duration
        duration_dif = timezone.now() - student_test.quizz_start_time
        duration = duration - duration_dif
        if duration.total_seconds() <= 0:
            student_test.quizz_duration = 0
        else:
            student_test.quizz_duration = duration
        student_test.save()
        data = self.list(request, *args, **kwargs).data
        duration = parse_duration(str(student_test.quizz_duration))
        return Response({
            "lessons": data,
            "duration": {
                "hour": duration.seconds // 3600,
                "minute": (duration.seconds % 3600) // 60,
                "seconds": duration.seconds % 60,
            }
        }, status=status.HTTP_200_OK)

    def get_queryset(self):
        student_quizz_id = self.kwargs.get('student_quizz')
        student_quizz = get_object_or_404(
            StudentQuizz.objects.select_related('lesson'), pk=student_quizz_id)

        queryset = self.queryset
        lesson = queryset.filter(pk=student_quizz.lesson_id).annotate(
            sum_of_questions=Count('student_quizz_questions',
                                   filter=Q(
                                       student_quizz_questions__student_quizz=student_quizz))
        )

        return lesson.order_by('-course_type_lessons__main', 'id')


by_lesson_quizz_lesson_view = ByLessonQuizLessonListView.as_view()


class ByLessonQuizQuestionListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.FullQuizQuestionSerializer
    queryset = Question.objects.select_related(
        'common_question').prefetch_related('answers').all()

    @swagger_auto_schema(tags=["by-lesson"],
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


by_lesson_quizz_question_view = ByLessonQuizQuestionListView.as_view()


class ByLessonPassAnswerView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.StudentAnswersSerializer

    @swagger_auto_schema(tags=["by-lesson"])
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


by_lesson_pass_answer_view = ByLessonPassAnswerView.as_view()


class ByLessonFinishView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(tags=["by-lesson"])
    def post(self, request, student_quizz):
        student_quizz = get_object_or_404(StudentQuizz, pk=student_quizz)
        if student_quizz.status in ["PASSED"]:
            raise PassedTestError()
        finish_full_test(student_quizz.id)
        # student_quizz = get_object_or_404(StudentQuizz, pk=student_quizz)
        # student_quizz.status = "PASSED"
        # student_quizz.quizz_end_time = datetime.now()
        # student_quizz.save()
        # test_full_score = []
        # question_score = StudentScore.objects.filter(
        #     student_quizz=student_quizz
        # ).exclude(status=False).distinct(). \
        #     aggregate(sum_score=Coalesce(Sum('score'), 0))
        # quantity_question = StudentQuizzQuestion.objects.filter(
        #     student_quizz=student_quizz).count()
        # ans_quantity_question = StudentScore.objects.filter(
        #     status=True,
        #     student_quizz=student_quizz,
        #     score__gt=0
        # ).values('question').annotate(
        #     count=Count('question')
        # ).count()
        # question_full_score = StudentQuizzQuestion.objects.filter(
        #     student_quizz=student_quizz,
        # ).distinct().aggregate(sum_score=Coalesce(
        #     Sum('question__lesson_question_level__question_level__point'), 0)
        # ).get("sum_score")
        # score = question_score.get('sum_score', 0)
        # test_full_score.append(
        #     TestFullScore(
        #         student_quizz=student_quizz,
        #         lesson=student_quizz.lesson,
        #         score=score,
        #         unattem=quantity_question - ans_quantity_question,
        #         number_of_score=question_full_score,
        #         number_of_question=quantity_question,
        #         accuracy=100 * score / question_full_score))
        # TestFullScore.objects.bulk_create(test_full_score)
        return Response({
            "detail": "success"
        }, status=status.HTTP_201_CREATED)


by_lesson_finish_view = ByLessonFinishView.as_view()


class ByLessonFinishInfoListView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.ResultScoreSerializer
    queryset = Question.objects.all().annotate(
        sum_score=Sum('question_score__score',
                      filter=Q(question_score__status=True))
    ).order_by('student_quizz_questions__order')

    @swagger_auto_schema(tags=["by-lesson"])
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
        quantity_correct_question = StudentScore.objects.filter(
            student_quizz=student_quizz_id,
            status=True,
            score__gt=0
        ).count()
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


by_lesson_result_view = ByLessonFinishInfoListView.as_view()


class ResultQuestionView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.QuestionResultSerializer
    queryset = Question.objects.all()
    lookup_field = 'pk'

    @swagger_auto_schema(tags=["by-lesson"])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


get_by_lesson_result_question = ResultQuestionView.as_view()


class GetTestFullScoreResultListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.TestFullScoreSerializer
    queryset = TestFullScore.objects.all()

    @swagger_auto_schema(tags=["by-lesson"])
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


get_by_lesson_full_score_result_view = GetTestFullScoreResultListView.as_view()


class ByLessonQuestionByTypeProgressView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(tags=["by-lesson"])
    def get(self, request, *args, **kwargs):
        student_quizz_id = self.kwargs.get('pk')
        questions = Question.objects.filter(
            student_quizz_questions__student_quizz_id=student_quizz_id,
        )
        score = StudentScore.objects.filter(student_quizz_id=student_quizz_id)

        choice_questions = questions.filter(
            question_type=QuestionType.DEFAULT,
            lesson_question_level__question_level__choice=ChoiceType.CHOICE,
            parent__isnull=True
        )
        choice_score = score.filter(
            question_id__in=[q.id for q in choice_questions]
        ).aggregate(sum_score=Coalesce(
            Sum('score'), 0)
        ).get("sum_score")
        choice = choice_questions.aggregate(sum_score=Coalesce(
            Sum('lesson_question_level__question_level__point'), 0)
        ).get("sum_score")

        multi_choice_questions = questions.filter(
            question_type=QuestionType.DEFAULT,
            lesson_question_level__question_level__choice=ChoiceType.MULTI_CHOICE
        )
        multi_choice = multi_choice_questions.aggregate(sum_score=Coalesce(
            Sum('lesson_question_level__question_level__point'), 0)
        ).get("sum_score")
        multi_choice_score = score.filter(
            question_id__in=[q.id for q in multi_choice_questions]
        ).aggregate(sum_score=Coalesce(
            Sum('score'), 0)
        ).get("sum_score")

        common_question = questions.filter(
            question_type=QuestionType.DEFAULT,
            common_question__isnull=False,
            parent__isnull=True
        )
        common = common_question.aggregate(sum_score=Coalesce(
            Sum('lesson_question_level__question_level__point'), 0)
        ).get("sum_score")
        common_score = score.filter(
            question_id__in=[q.id for q in common_question]
        ).aggregate(sum_score=Coalesce(
            Sum('score'), 0)
        ).get("sum_score")

        match_choice_questions = questions.filter(
            question_type=QuestionType.SELECT,
            parent__isnull=True
        )
        match_choice = match_choice_questions.aggregate(sum_score=Coalesce(
            Sum('lesson_question_level__question_level__point'), 0)
        ).get("sum_score")
        match_choice_score = score.filter(
            question_id__in=[q.id for q in match_choice_questions]
        ).aggregate(sum_score=Coalesce(
            Sum('score'), 0)
        ).get("sum_score")
        return Response({
            "choice": choice,
            "choice_score": choice_score,
            "common_question": common,
            "common_score": common_score,
            "multi_choice": multi_choice,
            "multi_choice_score": multi_choice_score,
            "match_choice": match_choice,
            "match_choice_score": match_choice_score,
        })


by_lesson_result_task_progress_view = ByLessonQuestionByTypeProgressView.as_view()
