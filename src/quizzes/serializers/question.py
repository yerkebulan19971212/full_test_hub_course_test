from rest_framework import serializers

from src.quizzes.serializers import AnswerSerializer
from src.quizzes.models import Question, CommonQuestion, TestFullScore


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = (
            'id',
            'question',
            'answers'
        )


class CommonQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommonQuestion
        fields = (
            'id',
            'text',
            'file'
        )


class FullQuizQuestionSerializer(serializers.ModelSerializer):
    answer = AnswerSerializer(source='answers', many=True)
    common_question = CommonQuestionSerializer(many=False)
    user_ans = serializers.SerializerMethodField()
    choice = serializers.IntegerField(
        source='lesson_question_level.question_level.choice')

    class Meta:
        model = Question
        fields = (
            'id',
            'question',
            'common_question',
            'choice',
            # 'number',
            'user_ans',
            'answer',
            'order',
        )

    def get_user_ans(self, obj):
        return [i.answer_id for i in obj.student_answers.all()]

class TestFullScoreSerializer(serializers.ModelSerializer):
    name_kz = serializers.CharField(source='lesson.name_kz')
    name_ru = serializers.CharField(source='lesson.name_ru')
    name_en = serializers.CharField(source='lesson.name_en')

    class Meta:
        model = TestFullScore
        fields = (
            'id',
            'lesson_id',
            'unattem',
            'score',
            'number_of_question',
            'number_of_score',
            'accuracy',
            'name_kz',
            'name_ru',
            'name_en',
        )


class ResultScoreSerializer(serializers.ModelSerializer):
    sum_score = serializers.IntegerField(default=None)

    class Meta:
        model = Question
        fields = (
            'id',
            'sum_score'
        )


class FullQuizQuestionQuerySerializer(serializers.Serializer):
    student_quizz_id = serializers.IntegerField(required=True)
    lesson_id = serializers.IntegerField(required=True)
