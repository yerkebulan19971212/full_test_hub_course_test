import django_filters
from django.db.models import Q
from django_filters import CharFilter, NumberFilter
from django_filters import rest_framework as filters

from src.common import models


class QuizzTypeFilter(django_filters.FilterSet):
    test_type = filters.CharFilter(
        field_name="course_type__name_code",
        required=True
    )

    class Meta:
        model = models.CourseTypeQuizz
        fields = (
            'test_type',
        )


class PacketFilter(django_filters.FilterSet):
    class Meta:
        model = models.Packet
        fields = (
            'quizz_type',
            'packet_type',
        )


class SchoolFilter(django_filters.FilterSet):
    class Meta:
        model = models.School
        fields = (
            'city',
        )