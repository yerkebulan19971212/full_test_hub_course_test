from django.db.models import Sum
from django.db.models.functions import Coalesce
from rest_framework import generics, status
from rest_framework import permissions
from rest_framework import views
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from src.quizzes.models import Question, Answer, StudentScore
from src.quizzes import serializers
from src.quizzes import filters
from src.quizzes.models.student_quizz import StudentQuizzQuestion, StudentQuizz


class NewQuizzTest(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.QuizzTestSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(tags=["quizz-test"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


new_quizz_test_view = NewQuizzTest.as_view()


class GetQuizTestQuestion(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.QuestionSerializer
    queryset = Question.objects.all()

    def get_object(self):
        student_quizz = self.kwargs['student_quizz']
        question = self.filter_queryset(
            queryset=Question.objects.get_question_for_quizz(
                self.kwargs['student_quizz'])
        ).first()
        StudentQuizzQuestion.objects.create(
            student_quizz_id=student_quizz,
            question=question
        )
        return question

    @swagger_auto_schema(tags=["quizz-test"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


get_quiz_test_question_view = GetQuizTestQuestion.as_view()


class PassQuizTestAnswerView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.QuizTestPassAnswerSerializer

    @swagger_auto_schema(tags=["quizz-test"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


pass_quizz_test_answer_view = PassQuizTestAnswerView.as_view()


class CheckQuizTestAnswerView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(tags=["quizz-test"])
    def post(self, request, *args, **kwargs):
        question_id = self.kwargs.get('question_id')
        answers = Answer.objects.filter(
            question_id=question_id,
            correct=True
        ).all()
        return Response(
            {"result": [ans.id for ans in answers]},
            status=status.HTTP_200_OK
        )


quiz_test_check_answer_view = CheckQuizTestAnswerView.as_view()


class FinishQuizTestAnswerView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(tags=["quizz-test"])
    def post(self, request, *args, **kwargs):
        student_quizz_id = self.kwargs.get('student_quizz')
        student_quizz = StudentQuizz.objects.get(pk=student_quizz_id)
        questions = Question.objects.filter(
            student_quizz_questions__student_quizz=student_quizz
        )
        number_of_score = questions.aggregate(
            number_of_score=Coalesce(
                Sum("lesson_question_level__question_level__point"),
                0
            )
        ).get("number_of_score")
        question_score = StudentScore.objects.filter(
            student_quizz=student_quizz,
            status=True
        )
        user_score = question_score.aggregate(
            user_score=Coalesce(Sum('score'), 0)
        ).get("user_score")
        attempt = question_score.values("question").distinct().count()
        question_count = questions.count()
        unattem = question_count - attempt

        data = {
            "user_score": user_score,
            "number_of_score": number_of_score,
            "incorrect_score": number_of_score - user_score,
            "accuracy": int(round(100 / number_of_score * user_score)),
            "attempt": question_count,
            "unattem": unattem,
            "question_number": question_count,
            "lesson_id": student_quizz.lesson_id,
            "lesson_name": student_quizz.lesson.name_kz,
        }

        return Response({
            "message": "Success",
            "result": data,
            "status_code": 0,
            "status": True
        }, status=status.HTTP_200_OK)


finish_quiz_test = FinishQuizTestAnswerView.as_view()
