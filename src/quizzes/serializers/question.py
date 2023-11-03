from rest_framework import serializers

from src.quizzes.serializers import AnswerSerializer, AnswerSignSerializer
from src.quizzes.models import Question, CommonQuestion, TestFullScore, \
    StudentAnswer, StudentQuizzQuestion


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


class QuestionResultSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()
    common_question = CommonQuestionSerializer(many=False)
    choice = serializers.IntegerField(
        source='lesson_question_level.question_level.choice')
    lesson = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()
    correct_answer = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = (
            'id',
            'question',
            'common_question',
            'choice',
            'answers',
            'lesson',
            'order',
            'correct_answer'
        )

    def get_order(self, obj):
        student_quizz_id = self.context.get('view').kwargs.get(
            'student_quizz_id')
        stq = StudentQuizzQuestion.objects.filter(
            student_quizz_id=student_quizz_id,
            question=obj
        ).first()
        order = StudentQuizzQuestion.objects.filter(
            student_quizz_id=student_quizz_id,
            lesson=stq.lesson
        ).order_by('order').first()
        return stq.order - order.order + 1

    def get_answers(self, obj):
        answers = obj.answers.all()
        answers_data = AnswerSignSerializer(answers, many=True).data
        student_quizz_id = self.context.get('view').kwargs.get(
            'student_quizz_id')
        for a in answers_data:
            ans_exists = StudentAnswer.objects.filter(
                student_quizz_id=student_quizz_id,
                question=obj,
                answer_id=a.get('id')
            ).first()
            if ans_exists:
                if ans_exists.answer.correct:
                    a["correct"] = "CORRECT"
                else:
                    a["correct"] = "WRONG"
            else:
                a["correct"] = "NOT_CHOOSE"
        return answers_data

    def get_lesson(self, obj):
        return obj.lesson_question_level.test_type_lesson.lesson.name_kz

    def get_correct_answer(self, obj):
        return [a.answer_sign.name_code for a in obj.answers.filter(correct=True)]
