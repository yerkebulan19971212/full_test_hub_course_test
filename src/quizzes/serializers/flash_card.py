import datetime

from rest_framework import serializers

from src.common.models import CourseType, QuizzType, CourseTypeQuizz
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
        validated_data["quizz_type"] = CourseTypeQuizz.objects.filter(
            quizz_type__name_code='flash_card').first()
        validated_data["course_type"] = CourseType.objects.get_ent()
        student_quizz = super().create(validated_data)
        questions = Question.objects.get_questions_for_flash_card(student_quizz.id, question_number)
        StudentQuizzQuestion.objects.bulk_create([StudentQuizzQuestion(
            question=q,
            student_quizz=student_quizz,
            lesson=student_quizz.lesson
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
            'id',
            'question',
            'answer'
        )

    def get_answer(self, obj):
        answers = obj.answers.all()
        return FlashCardAnswerSerializer(answers[0], many=False).data['answer']


class PassFlashCardQuestionSerializer(serializers.ModelSerializer):
    question = serializers.IntegerField(required=True)
    student_quizz = serializers.IntegerField(required=True)
    know_answer = serializers.BooleanField(required=True)

    class Meta:
        model = StudentQuizzQuestion
        fields = (
            'question',
            'student_quizz',
            'know_answer',
        )


class RepeatFlashCardQuizzSerializer(serializers.ModelSerializer):
    question_number = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = StudentQuizz
        fields = (
            'id',
            'language',
            'lesson',
            'question_number',
            'parent',
        )

    def create(self, validated_data):
        student_quizz_id = validated_data.get("parent")
        validated_data["quizz_start_time"] = datetime.datetime.now()
        validated_data["quizz_type"] = CourseTypeQuizz.objects.filter(
            quizz_type__name_code='flash_card').first()
        validated_data["course_type"] = CourseType.objects.get_ent()
        student_quizz = super().create(validated_data)
        know_questions = StudentQuizzQuestion.objects.filter(
            student_quizz_id=student_quizz_id,
            flash_card_status=False
        )
        StudentQuizzQuestion.objects.bulk_create([StudentQuizzQuestion(
            question=q.question,
            student_quizz=student_quizz
        ) for q in know_questions])

        return student_quizz
