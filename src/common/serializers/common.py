from rest_framework import serializers

from src.common import models
from src.common.abstract_serializer import NameSerializer
from src.common.models import Lesson, LessonPair


class QuizzTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QuizzType
        fields = (
            'id',
            'name_kz',
            'name_ru',
            'name_en',
            'icon',
            'color',
        )
