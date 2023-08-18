import django_filters
from django.db.models import Q
from django_filters import CharFilter, NumberFilter
from django_filters import rest_framework as filters

from src.common import models


class LessonFilter(django_filters.FilterSet):
    test_type = filters.NumberFilter(field_name="course_type__name_code")

    class Meta:
        model = models.Lesson
        fields = (
            'test_type',
            'math'
        )
