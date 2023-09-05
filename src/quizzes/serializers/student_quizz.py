import datetime

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from src.common import abstract_serializer
from src.common.models import CourseType, Lesson, QuizzType, LessonPair, \
    CourseTypeQuizz
from src.common.utils import get_multi_score
from src.quizzes.models import StudentQuizz, Question, Answer, StudentAnswer, \
    StudentScore
from src.quizzes.models.student_quizz import StudentQuizzQuestion


class ByLessonQuizzSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentQuizz
        fields = (
            'id',
            'language',
            'lesson',
            'quizz_type'
        )

    def create(self, validated_data):
        language = validated_data.get("language")
        lesson = validated_data.get("lesson")
        validated_data["quizz_start_time"] = datetime.datetime.now()
        validated_data["quizz_type"] = CourseTypeQuizz.objects.filter(
            quizz_type__name_code='by_lesson').first()
        course_type = CourseType.objects.get_ent()
        validated_data["course_type"] = course_type
        student_quizz = super().create(validated_data)
        questions = Question.objects.get_questions_by_lesson(lang=language,
                                                             lesson=lesson,
                                                             course_type=course_type.name_code)
        StudentQuizzQuestion.objects.bulk_create([StudentQuizzQuestion(
            question=q,
            lesson=lesson,
            student_quizz=student_quizz
        ) for q in questions])

        return student_quizz
