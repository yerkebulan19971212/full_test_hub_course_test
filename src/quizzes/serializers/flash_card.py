import datetime

from rest_framework import serializers

from src.common.constant import QuizzType, ChoiceType
from src.common.models import CourseType
from src.quizzes.models import StudentQuizz, Question
from src.quizzes.models.student_quizz import StudentQuizzQuestion


class FlashCardQuizzSerializer(serializers.ModelSerializer):
    lang = serializers.CharField(default="kz", write_only=True)
    lesson = serializers.IntegerField(required=True, write_only=True)
    question_number = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = StudentQuizz
        fields = (
            'id',
            'lang',
            'lesson',
            'question_number',
        )

    def create(self, validated_data):
        lesson = validated_data.pop("lesson")
        lang = validated_data.pop("lang")
        question_number = validated_data.pop("question_number")
        validated_data["lesson_id"] = lesson
        validated_data["quizz_start_time"] = datetime.datetime.now()
        validated_data["quizz_type"] = QuizzType.FLASH_CARD
        validated_data["course_type"] = CourseType.objects.get_ent()
        student_quizz = super().create(validated_data)
        questions = Question.objects.get_questions_for_flash_card(lang, lesson,
                                                                  question_number)
        StudentQuizzQuestion.objects.bulk_create([StudentQuizzQuestion(
            question=q,
            student_quizz=student_quizz
        ) for q in questions])

        return student_quizz


class FlashCardQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            'id',
            'question',
        )
