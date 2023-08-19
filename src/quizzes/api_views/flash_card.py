from rest_framework import generics
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend

from src.quizzes.models import Question
from src.quizzes import serializers
from src.quizzes import filters


class NewFlashCardQuizz(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.FlashCardQuizzSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


new_flash_card_view = NewFlashCardQuizz.as_view()


class GetFlashCardQuestions(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.QuestionSerializer
    queryset = Question.objects.get_questions_with_answer()
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.FlashCardQuestionFilter


get_flash_card_question = GetFlashCardQuestions.as_view()
