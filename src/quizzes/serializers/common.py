from rest_framework import serializers

from src.quizzes.serializers import AnswerSerializer
from src.quizzes.models import Question, CommonQuestion, StudentQuizz


class MyTestSerializer(serializers.ModelSerializer):
    quantity_question = serializers.IntegerField(default=120)

    class Meta:
        model = StudentQuizz
        fields = (
            'id',
            'quizz_start_time',
            'quizz_end_time',
            'status',
            'quizz_duration',
            'quantity_question'
        )
