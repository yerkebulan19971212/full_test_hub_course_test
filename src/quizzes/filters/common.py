from abc import ABC

import django_filters
from django.db.models import Q
from django_filters import CharFilter, NumberFilter
from django_filters import rest_framework as filters
from rest_framework import serializers

from src.common.models import CourseTypeQuizz
from src.quizzes import models


class MyTestFilter(django_filters.FilterSet):
    quizz_type = NumberFilter(method='quizz_type_filter')

    class Meta:
        model = models.StudentQuizz
        fields = (
            'quizz_type',
        )

    def quizz_type_filter(self, queryset, name, value):
        quizz_type = CourseTypeQuizz.objects.filter(pk=value).first()
        if quizz_type:
            if quizz_type.quizz_type.name_code == 'full_test':
                queryset = queryset.filter(
                    Q(quizz_type=quizz_type) |
                    Q(quizz_type__quizz_type__name_code='rating')
                )
            else:
                queryset = queryset.filter(Q(quizz_type=quizz_type))

        return queryset


class StudentQuizFileFilterSerializer(serializers.Serializer):
    file_type = serializers.CharField(default='full_test')


class RatingFilterSerializer(serializers.Serializer):
    q = serializers.CharField(required=False)
    school_id = serializers.IntegerField(required=False)
    lesson_pair_id = serializers.IntegerField(required=False)
    rating_period_id = serializers.IntegerField(required=False)


class MyLessonProgressFilter(django_filters.FilterSet):
    main = filters.BooleanFilter(
        field_name="lesson__course_type_lessons__main",
        required=True
    )

    class Meta:
        model = models.TestFullScore
        fields = (
            'main',
        )
