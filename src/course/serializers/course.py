from rest_framework import serializers

from src.course.models import Course


class CourseSerializer(serializers.ModelSerializer):
    content_count = serializers.IntegerField(default=0)

    class Meta:
        model = Course
        fields = (
            'uuid',
            'content_count',
            'main_img',
            'price',
            'name_kz',
            'name_ru',
            'name_en',
        )
