from rest_framework import serializers

from src.accounts.models import User
from src.common.abstract_serializer import NameSerializer
from src.course.models import Course, CourseTopic, Topic, CLesson, \
    CourseLessonType, CourseTopicLesson, Category


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'uuid',
            'first_name',
            'last_name'
        ]


class CategorySerializer(NameSerializer):
    parent = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'parent',
        )
        ref_name = 'CategorySerializer'

    def get_parent(self, obj):
        if obj.parent:
            serializer = CategorySerializer(obj.parent, context=self.context)
            return serializer.data
        return None


class CourseSerializer(serializers.ModelSerializer):
    content_count = serializers.IntegerField(default=0)
    owner = OwnerSerializer(read_only=True)
    teacher = OwnerSerializer(read_only=True)
    # category = CategorySerializer(read_only=True)

    class Meta:
        model = Course
        fields = (
            'uuid',
            'title',
            'content_count',
            'main_img',
            'price',
            'discount_price',
            'owner',
            'teacher',
            # 'category',
            'course_trailer',
            'duration',
        )


class CourseOneSerializer(serializers.ModelSerializer):
    content_count = serializers.IntegerField(default=0)
    teacher = OwnerSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Course
        fields = (
            'uuid',
            'title',
            'category',
            'content_count',
            'main_img',
            'price',
            'discount_price',
            'description',
            'teacher',
        )


class CourseCurriculumFilterSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()


class CourseLessonCurriculumSerializer(serializers.Serializer):
    course_lesson_type = serializers.FileField(
        source='course_lesson_type.icon')

    class Meta:
        model = CLesson
        fields = [
            'uuid',
            'course_lesson_type',
        ]


class CourseCurriculumSerializer(serializers.Serializer):
    course_lessons = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = (
            'uuid',
            'course_lessons',
        )

    def get_course_lessons(self, obj):
        course_lessons = []
        course_topics = obj.course_topic.all()
        for ct in course_topics:
            course_topic_lessons = ct.course_topic_lessons.all()
            for ctl in course_topic_lessons:
                course_lessons.append(ctl.course_lesson)
        if course_lessons:
            return CourseLessonCurriculumSerializer(course_lessons,
                                                    many=True,
                                                    context=self.context).data
        return course_lessons


class CourseLessonTypeSerializer(NameSerializer):
    class Meta:
        model = CourseLessonType
        fields = (
            'id',
            'name',
            'icon',
        )
        ref_name = 'CourseLessonTypeSerializer'


class CLessonSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='course_lesson.title')
    lesson_uuid = serializers.CharField(source='course_lesson.uuid')
    lesson_type = CourseLessonTypeSerializer(
        source='course_lesson.course_lesson_type')

    class Meta:
        model = CourseTopicLesson
        fields = [
            # 'lesson_id',
            'lesson_uuid',
            'lesson_type',
            'title',
            'order'
        ]
        ref_name = 'CLessonSerializer'


class CourseTopicCurriculumSerializer(serializers.ModelSerializer):
    # course_lessons = serializers.SerializerMethodField()
    title = serializers.CharField(source='topic.title', read_only=True)
    lessons = CLessonSerializer(source='course_topic_lessons', many=True)

    class Meta:
        model = CourseTopic
        fields = (
            'uuid',
            'title',
            'lessons',
        )

    def get_course_lessons(self, obj):
        course_lessons = []
        course_topic_lessons = obj.course_topic_lessons.all()
        for ctl in course_topic_lessons:
            course_lessons.append(ctl.course_lesson)
        if course_lessons:
            return CourseLessonCurriculumSerializer(course_lessons,
                                                    many=True,
                                                    context=self.context).data
        return course_lessons


class CourseCurriculumUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = (
            'uuid',
            # 'name_kz',
            # 'name_ru',
            # 'name_en',
        )


class CourseLessonUserSerializer(serializers.ModelSerializer):
    passed = serializers.BooleanField()

    class Meta:
        model = CLesson
        fields = (
            'uuid',
            # 'name_kz',
            # 'name_ru',
            # 'name_en',
            'passed'
        )
