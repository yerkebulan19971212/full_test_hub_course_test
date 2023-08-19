from rest_framework import serializers

from src.quizzes.serializers import AnswerSerializer
from src.quizzes.models import Question


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = (
            'id',
            'question',
            'answers'
        )
