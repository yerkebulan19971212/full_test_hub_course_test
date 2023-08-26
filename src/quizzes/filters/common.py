import django_filters
from django.db.models import Q
from django_filters import CharFilter, NumberFilter
from django_filters import rest_framework as filters

from src.quizzes import models


class MyTestFilter(django_filters.FilterSet):

    class Meta:
        model = models.StudentQuizz
        fields = (
            'quizz_type'
        )
