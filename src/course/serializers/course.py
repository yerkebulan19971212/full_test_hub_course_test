from rest_framework import serializers

from src.accounts.models import User
from src.course.models import Course, CourseTopic, Topic, CLesson, CourseLessonType


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'uuid',
            'first_name',
            'last_name'
        ]


class CourseSerializer(serializers.ModelSerializer):
    content_count = serializers.IntegerField(default=0)
    owner = OwnerSerializer(read_only=True)

    class Meta:
        model = Course
        fields = (
            'uuid',
            'content_count',
            'main_img',
            'price',
            'owner',
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
    course_lesson_type = serializers.FileField(source='course_lesson_type.icon')

    class Meta:
        model = CLesson
        fields = [
            'uuid',
            'course_lesson_type',
            'name_kz',
            'name_ru',
            'name_en',
        ]


class CourseCurriculumSerializer(serializers.ModelSerializer):
    # course_lesson = CourseLessonCurriculumSerializer(source='course_topic_lessons__course_lesson')
    course_lessons = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = (
            'uuid',
            'course_lessons',
            'name_kz',
            'name_ru',
            'name_en',
        )

    def get_course_lessons(self, obj):
        course_lessons = []
        course_topics = obj.course_topic.all()
        for ct in course_topics:
            course_topic_lessons = ct.course_topic_lessons.all()
            for ctl in course_topic_lessons:
                course_lessons.append(ctl.course_lesson)
        if course_lessons:
            return CourseLessonCurriculumSerializer(course_lessons, many=True).data
        return course_lessons
