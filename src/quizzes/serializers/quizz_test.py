import datetime

from rest_framework import serializers

from src.common.constant import QuizzType, ChoiceType
from src.common.models import CourseType
from src.quizzes.models import StudentQuizz, Question, Answer, StudentAnswer, \
    StudentScore
from src.quizzes.models.student_quizz import StudentQuizzQuestion


class QuizzTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentQuizz
        fields = (
            'id',
            'language',
            'lesson',
        )

    def create(self, validated_data):
        validated_data["quizz_start_time"] = datetime.datetime.now()
        validated_data["quizz_type"] = QuizzType.INFINITY_QUIZ
        validated_data["course_type"] = CourseType.objects.get_ent()
        return super().create(validated_data)


class QuizTestPassAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = (
            'id',
            'student_quizz',
            'question',
            'answer',
        )

    def create(self, validated_data):
        student_quizz = validated_data["student_quizz"]
        question = validated_data["question"]
        answer = validated_data["answer"]
        StudentAnswer.objects.filter(
            student_quizz=student_quizz,
            question=question,
        ).update(status=False)
        if answer.correct:
            StudentScore.objects.filter(
                student_quizz=student_quizz,
                question=question
            ).update(status=False)
            StudentScore.objects.create(
                student_quizz=student_quizz,
                question=question,
                score=question.lesson_question_level.question_level.point
            )

        return super().create(validated_data)
