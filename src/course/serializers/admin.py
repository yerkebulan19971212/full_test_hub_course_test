from rest_framework import serializers

from src.common.abstract_serializer import NameSerializer
from src.course.models import Course, Category, CourseTopic, Topic, CLesson, \
    CourseLessonType
from src.course.models.c_lesson import CLessonContent, CourseTopicLesson


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
            'id',
            'name',
            'parent',
            'children'
        )


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            'id',
            'title',
            'category',
            'language',
            'duration',
            'price',
            'discount_price',
            'discount_percent',
            'number_of_students',
            'course_trailer',
            'main_img',
            'description',
        )

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class CourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            'id',
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
    title = serializers.CharField(source='topic.title')

    class Meta:
        model = CourseTopic
        fields = (
            'title',
        )

    def update(self, instance, validated_data):
        title = validated_data.get('topic').get('title')
        topic = instance.topic
        topic.title = title
        topic.save()
        return instance


class CLessonSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='course_lesson.title')
    lesson_uuid = serializers.CharField(source='course_lesson.uuid')

    class Meta:
        model = CourseTopicLesson
        fields = [
            # 'uuid',
            'lesson_uuid',
            'title',
            'order'
        ]


class CourseTopicListSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='topic.title', read_only=True)
    lessons = CLessonSerializer(source='course_topic_lessons', many=True)

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


class CreateCLessonSerializer(serializers.ModelSerializer):
    course_topic_uuid = serializers.UUIDField(required=True, write_only=True)
    course_lesson_type = CourseLessonTypeSerializer()
    c_lesson_contents = ContentLessonSerializer(many=True, read_only=True)

    class Meta:
        model = CLesson
        fields = (
            'title',
            'course_topic_uuid',
            'course_lesson_type',
            'duration',
            'c_lesson_contents'
        )

    def create(self, validated_data):
        course_topic_uuid = validated_data.pop('course_topic_uuid')
        course_topic = CourseTopic.objects.get(uuid=course_topic_uuid)
        lesson = super().create(validated_data)
        CourseTopicLesson.objects.create(
            owner=course_topic.owner,
            course_lesson=lesson,
            course_topic=course_topic
        )
        return lesson


class CreateContentLessonSerializer(serializers.ModelSerializer):
    course_lesson_type = CourseLessonTypeSerializer()
    lesson_uuid = serializers.UUIDField(required=True, write_only=True)

    class Meta:
        model = CLessonContent
        fields = (
            'course_lesson_type',
            'text',
            'video',
            'img',
            'file',
            'lesson_uuid'
        )

    def create(self, validated_data):
        lesson_uuid = validated_data.pop('lesson_uuid')
        c_lesson = CLesson.objects.get(uuid=lesson_uuid)
        validated_data['course_lesson'] = c_lesson
        validated_data['owner'] = c_lesson.owner
        return super().create(validated_data)
