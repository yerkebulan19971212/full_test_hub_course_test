import django_filters
from django.db.models import Q
from django_filters import CharFilter, NumberFilter
from django_filters import rest_framework as filters

from src.common import models


class LessonFilter(django_filters.FilterSet):
    test_type = filters.CharFilter(
        field_name="course_type_lessons__course_type__name_code")
    main = filters.BooleanFilter(field_name="course_type_lessons__main")
    without_creative = filters.BooleanFilter(
        method="get_without_creative", required=False)

    class Meta:
        model = models.Lesson
        fields = (
            'test_type',
            'math',
            'main'
        )

    @staticmethod
    def get_without_creative(queryset, name, value):
        if value:
            return queryset.exclude(name_code='creative_exam')
        return queryset
