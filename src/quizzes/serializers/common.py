from rest_framework import serializers

from src.quizzes.serializers import AnswerSerializer
from src.quizzes.models import Question, CommonQuestion, StudentQuizz


class MyTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentQuizz
        fields = (
            'id',
            'quizz_start_time',
            'quizz_end_time',
            'status'
        )
