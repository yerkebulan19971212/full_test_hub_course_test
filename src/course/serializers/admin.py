from rest_framework import serializers

from src.common.abstract_serializer import NameSerializer
from src.course.models import Course, Category, CourseTopic, Topic, CLesson, \
    CourseLessonType
from src.course.models.c_lesson import CLessonContent


class CourseLessonTypeSerializer(NameSerializer):
    class Meta:
        model = CourseLessonType
        fields = (
            'uuid',
            'name',
            'icon',
        )


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


class TopicCreateSerializer(serializers.ModelSerializer):
    course_uuid = serializers.UUIDField(required=True, write_only=True)

    class Meta:
        model = Topic
        fields = (
            'title',
            'course_uuid',
        )

    def create(self, validated_data):
        order = 1
        course_uuid = validated_data.pop('course_uuid')
        course = Course.api_objects.get(uuid=course_uuid)
        course_topic = CourseTopic.api_objects.all_active().filter(
            course=course
        ).order_by('order')
        if course_topic.exists():
            order = course_topic.last().order + 1
        validated_data['owner'] = course.owner
        validated_data['order'] = order
        topic = super().create(validated_data)
        CourseTopic.objects.create(
            owner=course.owner,
            course=course,
            topic=topic,
            order=order
        )
        return topic


class CourseTopicCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField()

    class Meta:
        model = Topic
        fields = (
            'title',
        )

    def update(self, instance, validated_data):
        title = validated_data.pop('title')
        topic = instance.topic
        topic.title = title
        topic.save()
        return instance


class CLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = CLesson
        fields = [
            'uuid',
            'title',
            'order'
        ]


class CourseTopicListSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='topic.title', read_only=True)
    lessons = CLessonSerializer(source='course_topic_lessons')

    class Meta:
        model = CourseTopic
        fields = (
            'uuid',
            'title',
            'order',
            'lessons'
        )


class CLessonContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CLessonContent
        fields = [
            'uuid',
            'uuid',
            'uuid',
        ]


class ContentLessonSerializer(serializers.ModelSerializer):
    course_lesson_type = CourseLessonTypeSerializer()

    class Meta:
        model = CLessonContent
        fields = (
            'course_lesson_type',
            'text',
            'video',
            'img',
            'file',
            'course_lesson'
        )


class CreateCLessonSerializer(NameSerializer):
    lesson_contents = ContentLessonSerializer()

    class Meta:
        model = CLesson
        fields = (
            'title',
            'course_lesson_type',
            'duration',
            'lesson_contents'
        )


class CreateContentLessonSerializer(serializers.ModelSerializer):
    course_lesson_type = CourseLessonTypeSerializer()

    class Meta:
        model = CLessonContent
        fields = (
            'course_lesson_type',
            'text',
            'video',
            'img',
            'file',
            'course_lesson'
        )
