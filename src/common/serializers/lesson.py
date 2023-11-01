from django.db.models import Q
from rest_framework import serializers

from src.common.abstract_serializer import NameSerializer
from src.common.models import Lesson, LessonPair


class LessonSerializer(NameSerializer):
    class Meta:
        model = Lesson
        fields = (
            'id',
            'name',
            'choose_icon',
            'icon'
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


class LessonWithPairsSerializer(NameSerializer):
    lessons = serializers.SerializerMethodField()
    main = serializers.BooleanField()

    class Meta:
        model = Lesson
        fields = (
            'id',
            'icon',
            'main',
            'choose_icon',
            'name',
            'lessons',
        )

    def get_lessons(self, obj):
        l = (list(set([l.id for l in Lesson.objects.filter(
            Q(lesson_1__lesson_1_id=obj.id) |
            Q(lesson_1__lesson_2_id=obj.id) |
            Q(lesson_2__lesson_1_id=obj.id) |
            Q(lesson_2__lesson_2_id=obj.id)
        )])))
        if l:
            l.remove(obj.id)
        return l
