from rest_framework import serializers

from src.common.abstract_serializer import NameSerializer
from src.common.models import Lesson, LessonPair


class LessonSerializer(NameSerializer):
    class Meta:
        model = Lesson
        fields = (
            'id',
            'name',
        )


class LessonPairListSerializer(serializers.ModelSerializer):
    lesson_1 = LessonSerializer(read_only=True, many=False)
    lesson_2 = LessonSerializer(read_only=True, many=False)

    class Meta:
        model = LessonPair
        fields = (
            'id',
            'icon',
            'lesson_1',
            'lesson_2'
        )
