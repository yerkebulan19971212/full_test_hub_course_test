import django_filters
from django.db.models import Q
from django_filters import CharFilter, NumberFilter
from django_filters import rest_framework as filters

from src.quizzes import models


class FlashCardQuestionFilter(django_filters.FilterSet):
    student_quizz_id = filters.NumberFilter(
        field_name="student_quizz_questions__student_quizz_id")

    class Meta:
        model = models.Question
        fields = (
            'student_quizz_id',
        )


class StudentQuizQuestionFilter(django_filters.FilterSet):
    student_quizz_id = filters.NumberFilter(
        field_name="student_quizz_questions__student_quizz_id")

    class Meta:
        model = models.Question
        fields = (
            'student_quizz_id',
        )