from rest_framework import serializers

from src.accounts.models import User
from src.common.abstract_serializer import NameSerializer
from src.common.constant import CourseStatus
from src.common.exception import NotEnoughBalance
from src.course.models import Course, CourseTopic, Topic, CLesson, \
    CourseLessonType, CourseTopicLesson, Category
from src.course.models.c_lesson import CLessonContent, UserCLesson
from src.course.models.course import UserCourse


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
    passed_lesson_count = serializers.SerializerMethodField()
    all_lesson_count = serializers.SerializerMethodField()
    passed_percent = serializers.SerializerMethodField()
    mine = serializers.BooleanField(default=False)

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
            'passed_percent',
            'course_trailer',
            'duration',
            'passed_lesson_count',
            'passed_percent',
            'all_lesson_count',
            'mine',
        )

    def get_passed_lesson_count(self, obj):
        return UserCLesson.objects.filter(
            course_lesson__course_topic_lessons__course_topic__course=obj,
            passed=True,
            user=self.context['request'].user
        ).count()

    def get_passed_percent(self, obj):
        passed = UserCLesson.objects.filter(
            course_lesson__course_topic_lessons__course_topic__course=obj,
            passed=True,
            user=self.context['request'].user
        ).count()
        all = CLesson.objects.filter(
            course_topic_lessons__course_topic__course=obj
        ).count()
        if all == 0:
            return 0
        return passed / all * 100

    def get_all_lesson_count(self, obj):
        return CLesson.objects.filter(
            course_topic_lessons__course_topic__course=obj
        ).count()


class CourseOneSerializer(serializers.ModelSerializer):
    content_count = serializers.IntegerField(default=0)
    teacher = OwnerSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    passed_lesson_count = serializers.SerializerMethodField()
    all_lesson_count = serializers.SerializerMethodField()
    passed_percent = serializers.SerializerMethodField()
    mine = serializers.BooleanField(default=False)

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
            'number_of_students',
            'course_trailer',
            'duration',
            'passed_lesson_count',
            'passed_percent',
            'all_lesson_count',
            'mine',
        )

    def get_passed_lesson_count(self, obj):
        return UserCLesson.objects.filter(
            course_lesson__course_topic_lessons__course_topic__course=obj,
            passed=True,
            user=self.context['request'].user
        ).count()

    def get_passed_percent(self, obj):
        passed = UserCLesson.objects.filter(
            course_lesson__course_topic_lessons__course_topic__course=obj,
            passed=True,
            user=self.context['request'].user
        ).count()
        all = CLesson.objects.filter(
            course_topic_lessons__course_topic__course=obj
        ).count()
        if all == 0:
            return 0
        return passed / all * 100

    def get_all_lesson_count(self, obj):
        return CLesson.objects.filter(
            course_topic_lessons__course_topic__course=obj
        ).count()


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
            'lesson_uuid',
            'lesson_type',
            'title',
            'order'
        ]
        ref_name = 'CLessonSerializer'


class CLessonUserSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='course_lesson.title')
    lesson_uuid = serializers.CharField(source='course_lesson.uuid')
    lesson_type = CourseLessonTypeSerializer(
        source='course_lesson.course_lesson_type')
    status = serializers.BooleanField(default=False)

    class Meta:
        model = CourseTopicLesson
        fields = [
            'lesson_uuid',
            'lesson_type',
            'title',
            'order',
            'status',
        ]
        ref_name = 'CLessonSerializerUser'


class CourseTopicCurriculumSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='topic.title', read_only=True)
    lessons = CLessonSerializer(source='course_topic_lessons', many=True)

    class Meta:
        model = CourseTopic
        fields = (
            'uuid',
            'title',
            'lessons',
        )


class CourseCurriculumUserSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='topic.title', read_only=True)
    lessons = CLessonUserSerializer(source='course_topic_lessons', many=True)
    status = serializers.BooleanField(default=False)

    class Meta:
        model = CourseTopic
        fields = (
            'uuid',
            'title',
            'lessons',
            'status',
        )


class GetContentLessonSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id',
            'name',
            'order',
            'text',
            'video',
            'img',
            'file',
        )
        model = CLessonContent
        ref_name = 'GetContentLessonSerializer'

    def get_name(self, obj):
        language = self.context.get('request').headers.get('language', 'kz')
        if language == 'kz':
            return obj.course_lesson_type.name_kz
        elif language == 'en':
            return obj.course_lesson_type.name_ru
        return obj.course_lesson_type.name_ru


class CourseLessonUserSerializer(serializers.ModelSerializer):
    passed = serializers.SerializerMethodField(default=False)
    lesson_contents = GetContentLessonSerializer(source='c_lesson_contents',
                                                 read_only=True, many=True)

    class Meta:
        model = CLesson
        fields = (
            'uuid',
            # 'name_kz',
            # 'name_ru',
            # 'name_en',
            'title',
            'passed',
            'lesson_contents'
        )

    def get_passed(self, obj):
        user_lesson = UserCLesson.objects.filter(
            course_lesson=obj,
            user=self.context['request'].user)
        if user_lesson.exists():
            return user_lesson.first().passed
        return False


class BuyCourseSerializer(serializers.ModelSerializer):
    course_uuid = serializers.UUIDField(write_only=True)

    class Meta:
        model = UserCourse
        fields = (
            'id',
            'uuid',
            'course_uuid',
        )

    def create(self, validated_data):
        course_uuid = validated_data.pop('course_uuid')
        course = Course.objects.get(uuid=course_uuid)
        price = course.discount_price if course.discount_price > 0 else course.price
        user = self.context['request'].user
        if user.balance < price:
            raise NotEnoughBalance()
        validated_data['course'] = course
        validated_data['user'] = user
        validated_data['price'] = price
        user.balance -= price
        user.save()
        user_course = UserCourse.objects.filter(
            course=course,
            user=user,
            status__in=[
                CourseStatus.NOT_PASSED,
                CourseStatus.CONTINUE
            ]

        )
        if user_course.exists():
            user_course = user_course.first()
        else:
            user_course = super().create(validated_data)
            c_lesson_list = CLesson.objects.filter(
                course_topic_lessons__course_topic__course=course
            )
            user_lesson_list = []
            for lesson in c_lesson_list:
                user_lesson_list.append(UserCLesson(
                    user=user,
                    course_lesson=lesson,
                ))
            UserCLesson.objects.bulk_create(user_lesson_list)
        return user_course


class UserCourseInfoSerializer(serializers.ModelSerializer):
    content_count = serializers.IntegerField(default=0)
    passed_percent = serializers.IntegerField(default=0)
    teacher = OwnerSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Course
        fields = (
            'uuid',
            'title',
            'category',
            'content_count',
            'passed_percent',
            'main_img',
            'price',
            'discount_price',
            'description',
            'teacher',
            'number_of_students',
            'course_trailer',
            'duration',
        )


class UserCoursePassSerializer(serializers.Serializer):
    lesson_uuid = serializers.UUIDField()


class AllCourseFilterSerializer(serializers.Serializer):
    mine = serializers.BooleanField(default=False)
