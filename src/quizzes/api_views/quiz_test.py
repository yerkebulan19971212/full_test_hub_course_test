from rest_framework import generics
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema

from src.quizzes.models import Question
from src.quizzes import serializers
from src.quizzes import filters
from src.quizzes.models.student_quizz import StudentQuizzQuestion



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
