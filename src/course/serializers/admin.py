from rest_framework import serializers

from src.common.abstract_serializer import NameSerializer
from src.course.models import Course, Category, CourseTopic, Topic, CLesson, \
    CourseLessonType
from src.course.models.c_lesson import CLessonContent, CourseTopicLesson


class CourseLessonTypeSerializer(NameSerializer):
    class Meta:
        model = CourseLessonType
        fields = (
            'id',
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
    discount_price = serializers.IntegerField(default=0)
    discount_percent = serializers.IntegerField(default=0)
    number_of_students = serializers.IntegerField(default=0)
    parent_category = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Course
        fields = (
            'id',
            'title',
            'teacher',
            'category',
            'parent_category',
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

    def get_parent_category(self, obj):
        parent_id = obj.category.parent_id
        if parent_id:
            return parent_id
        return None


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
    course_id = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = Topic
        fields = (
            'title',
            'course_id',
        )

    def create(self, validated_data):
        order = 1
        course_id = validated_data.pop('course_id')
        course = Course.api_objects.get(id=course_id)
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
    lesson_id = serializers.CharField(source='course_lesson_id')

    class Meta:
        model = CourseTopicLesson
        fields = [
            # 'uuid',
            'lesson_id',
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
            'id',
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


class GetContentLessonSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id',
            'name',
            'order',
        )
        model = CLessonContent

    def get_name(self, obj):
        language = self.context.get('request').headers.get('language', 'kz')
        if language == 'kz':
            return obj.course_lesson_type.name_kz
        elif language == 'en':
            return obj.course_lesson_type.name_ru
        return obj.course_lesson_type.name_ru


class ContentLessonSerializer(serializers.ModelSerializer):
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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        course_lesson_type = instance.course_lesson_type
        if course_lesson_type:
            serializer = CourseLessonTypeSerializer(
                course_lesson_type,
                context=self.context
            )
            data['course_lesson_type'] = serializer.data
        return data


class CreateCLessonSerializer(serializers.ModelSerializer):
    topic_id = serializers.IntegerField(required=True, write_only=True)
    # course_lesson_type = CourseLessonTypeSerializer()
    c_lesson_contents = GetContentLessonSerializer(many=True, read_only=True)

    class Meta:
        model = CLesson
        fields = (
            'id',
            'title',
            'topic_id',
            'course_lesson_type',
            'duration',
            'c_lesson_contents'

        )

    def create(self, validated_data):
        course_topic_uuid = validated_data.pop('topic_id')
        course_topic = CourseTopic.objects.get(pk=course_topic_uuid)
        lesson = super().create(validated_data)
        CourseTopicLesson.objects.create(
            owner=course_topic.owner,
            course_lesson=lesson,
            course_topic=course_topic
        )
        return lesson

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     course_lesson_type = instance.course_lesson_type
    #     if course_lesson_type:
    #         serializer = CourseLessonTypeSerializer(course_lesson_type, context=self.context)
    #         data['course_lesson_type'] = serializer.data
    #     return data


class CreateContentLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = CLessonContent
        fields = (
            'id',
            'course_lesson_type',
            'text',
            'video',
            'img',
            'file',
            'course_lesson'
        )

    def update(self, instance, validated_data):
        course_lesson = validated_data.get('course_lesson')
        validated_data['owner'] = course_lesson.owner
        return super().update(instance, validated_data)

    def create(self, validated_data):
        course_lesson = validated_data.get('course_lesson')
        print(course_lesson)
        print("========course_lesson")
        validated_data['owner'] = course_lesson.owner
        return super().create(validated_data)


class OrderUpdateInstanceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    order = serializers.IntegerField()


class OrderUpdateSerializer(serializers.Serializer):
    name = serializers.CharField()
    order_list = serializers.ListField(child=OrderUpdateInstanceSerializer())
