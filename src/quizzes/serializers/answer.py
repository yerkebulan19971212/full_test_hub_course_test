from rest_framework import serializers
from src.quizzes.models import Answer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = (
            'id',
            'answer',
        )


class AnswerSignSerializer(serializers.ModelSerializer):
    sign = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = (
            'id',
            'answer',
            'sign'
        )

    def get_sign(self, obj):
        return obj.answer_sign.name_code
