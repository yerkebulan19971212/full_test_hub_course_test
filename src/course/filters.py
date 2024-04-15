from abc import ABC

import django_filters
from django.db.models import Q
from django_filters import CharFilter, NumberFilter
from django_filters import rest_framework as filters
from rest_framework import serializers

from src.course import models


class CourseTopicFilter(django_filters.FilterSet):
    course = filters.UUIDFilter(field_name='course__uuid')

    class Meta:
        model = models.CourseTopic
        fields = (
            'course',
        )
