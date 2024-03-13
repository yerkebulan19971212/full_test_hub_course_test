from rest_framework import serializers

from src.course.models import Course, CourseTopic, Topic, CLesson, CourseLessonType


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


class CourseOneSerializer(serializers.ModelSerializer):
    content_count = serializers.IntegerField(default=0)

    class Meta:
        model = Course
        fields = (
            'uuid',
            'content_count',
            'main_img',
            'price',
            'description',
            'name_kz',
            'name_ru',
            'name_en',
        )


class CourseCurriculumFilterSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()


class CourseLessonCurriculumSerializer(serializers.ModelSerializer):
    # course_lesson_type = serializers.FileField(source='course_lesson_type.icon')

    class Meta:
        model = CLesson
        fields = [
            'uuid',
            # 'course_lesson_type',
            'name_kz',
            'name_ru',
            'name_en',
        ]


class CourseCurriculumSerializer(serializers.ModelSerializer):
    course_lessons = CourseLessonCurriculumSerializer(source='course_topic_lessons__course_lesson')

    class Meta:
        model = Topic
        fields = (
            'uuid',
            'course_lessons',
            'name_kz',
            'name_ru',
            'name_en',
        )
