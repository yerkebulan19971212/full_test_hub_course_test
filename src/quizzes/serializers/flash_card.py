import datetime

from rest_framework import serializers

from src.common.constant import QuizzType, ChoiceType
from src.common.models import CourseType
from src.quizzes.models import StudentQuizz, Question, Answer
from src.quizzes.models.student_quizz import StudentQuizzQuestion


class FlashCardQuizzSerializer(serializers.ModelSerializer):
    question_number = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = StudentQuizz
        fields = (
            'id',
            'language',
            'lesson',
            'question_number',
        )

    def create(self, validated_data):
        lesson = validated_data.get("lesson")
        language = validated_data.get("language")
        question_number = validated_data.pop("question_number")
        validated_data["quizz_start_time"] = datetime.datetime.now()
        validated_data["quizz_type"] = QuizzType.FLASH_CARD
        validated_data["course_type"] = CourseType.objects.get_ent()
        student_quizz = super().create(validated_data)
        questions = Question.objects.get_questions_for_flash_card(language,
                                                                  lesson,
                                                                  question_number)
        StudentQuizzQuestion.objects.bulk_create([StudentQuizzQuestion(
            question=q,
            student_quizz=student_quizz
        ) for q in questions])

        return student_quizz


class FlashCardAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = (
            'answer',
        )


class FlashCardQuestionSerializer(serializers.ModelSerializer):
    answer = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = (
            'question',
            'answer'
        )

    def get_answer(self, obj):
        answers = obj.answers.all()
        return FlashCardAnswerSerializer(answers[0], many=False).data['answer']
