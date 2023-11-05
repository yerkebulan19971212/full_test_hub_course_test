from datetime import datetime

from rest_framework import generics, status
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import views

from src.common.constant import QuizzStatus
from src.quizzes.models import Question, StudentQuizz, StudentQuizzQuestion
from src.quizzes import serializers
from src.quizzes import filters


class NewFlashCardQuizz(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.FlashCardQuizzSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(tags=["flash-card"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


new_flash_card_view = NewFlashCardQuizz.as_view()


class GetFlashCardQuestions(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.FlashCardQuestionSerializer
    queryset = Question.objects.get_questions_with_correct_answer()
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.FlashCardQuestionFilter

    @swagger_auto_schema(tags=["flash-card"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


get_flash_card_question = GetFlashCardQuestions.as_view()


class PassFlashCardQuestions(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.PassFlashCardQuestionSerializer

    @swagger_auto_schema(tags=["flash-card"])
    def post(self, request, *args, **kwargs):
        question = self.request.data.get("question")
        know_answer = self.request.data.get("know_answer")
        student_quizz_id = self.request.data.get("student_quizz")
        student_quizz = StudentQuizz.objects.get(pk=student_quizz_id)
        student_quizz_question = StudentQuizzQuestion.objects.filter(
            question=question,
            student_quizz=student_quizz,
            lesson=student_quizz.lesson
        ).first()
        student_quizz_question.flash_card_status = know_answer
        student_quizz_question.save()
        return Response()


pass_flash_card_question = PassFlashCardQuestions.as_view()


class FinishFlashCardView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(tags=["quizz-test"])
    def post(self, request, *args, **kwargs):
        student_quizz_id = self.kwargs.get('student_quizz')
        student_quizz = StudentQuizz.objects.get(pk=student_quizz_id)
        student_quizz.status = QuizzStatus.PASSED
        student_quizz.quizz_end_time = datetime.now()
        student_quizz.save()

        return Response()


finish_flash_card_view = FinishFlashCardView.as_view()


class ResultFlashCardQuestions(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.PassFlashCardQuestionSerializer

    @swagger_auto_schema(tags=["flash-card"])
    def get(self, request, *args, **kwargs):
        student_quizz_id = self.kwargs.get('student_quizz')
        student_quizz = StudentQuizz.objects.get(pk=student_quizz_id)
        student_quizz_questions = StudentQuizzQuestion.objects.filter(
            student_quizz=student_quizz,
        )
        question_count = student_quizz_questions.count()
        know_question_count = student_quizz_questions.filter(
            flash_card_status=True).count()
        total_time = student_quizz.quizz_end_time - student_quizz.quizz_start_time
        total_time_seconds = (
                total_time - datetime(1970, 1, 1)).total_seconds()
        average_seconds = int(round(total_time_seconds / question_count))
        accuracy = int(round(100 / question_count * know_question_count))
        return Response({
            "total_time": total_time_seconds,
            "average_seconds": average_seconds,
            "user_score": know_question_count,
            "number_of_score": question_count,
            "accuracy": accuracy,
            "inaccuracy": 100 - accuracy,
        }, status=status.HTTP_200_OK)


result_flash_card_question = ResultFlashCardQuestions.as_view()


class RepeatFlashCardQuizzView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.FlashCardQuizzSerializer

    def perform_create(self, serializer):
        student_quizz_id = self.kwargs.get('student_quizz')
        student_quizz = StudentQuizz.objects.get(pk=student_quizz_id)
        know_question_count = StudentQuizzQuestion.objects.filter(
            student_quizz=student_quizz,
            flash_card_status=False).count()
        serializer.save(
            user=self.request.user,
            lesson=student_quizz.lesson,
            language=student_quizz.language,
            question_number=know_question_count,
            parent=student_quizz_id
        )

    @swagger_auto_schema(tags=["flash-card"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


repeat_flash_card_view = RepeatFlashCardQuizzView.as_view()
