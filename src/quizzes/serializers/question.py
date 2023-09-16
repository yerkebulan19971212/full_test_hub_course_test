from rest_framework import serializers

from src.quizzes.serializers import AnswerSerializer
from src.quizzes.models import Question, CommonQuestion, StudentScore, \
    TestFullScore


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
            'answer'
        )

    def get_user_ans(self, obj):
        return [i.answer_id for i in obj.student_answers.all()]


class ResultScoreSerializer(serializers.ModelSerializer):
    sum_score = serializers.IntegerField(default=None)

    class Meta:
        model = Question
        fields = (
            'id',
            'sum_score'
        )
