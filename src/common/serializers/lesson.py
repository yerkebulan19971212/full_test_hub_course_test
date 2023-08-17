from rest_framework import serializers

from src.common.abstract_serializer import NameSerializer
from src.common.models import Lesson


class LessonSerializer(NameSerializer):

    class Meta:
        model = Lesson
        fields = (
            'uuid_field',
            'name',
        )