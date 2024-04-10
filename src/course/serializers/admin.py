from rest_framework import serializers

from src.common.abstract_serializer import NameSerializer
from src.course.models import Course, Category


class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CategorySerializer(NameSerializer):
    children = RecursiveSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = (
            'uuid',
            'name',
            'parent',
            'children'
        )


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            'title',
            'category',
            'language',
            'duration',
            'owner',
            'price',
            'discount_price',
            'discount_percent',
            'number_of_students',
            'course_trailer',
            'main_img',
            'description',
        )


class CourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            'uuid',
            'title',
            'main_img',
        )
