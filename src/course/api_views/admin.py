import datetime

from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend

from src.course.models import Category, Course, CourseTopic, CourseLessonType, \
    CLesson, CourseTopicLesson
from src.course import serializers, filters


class CourseLessonTypeListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = CourseLessonType.objects.filter(
        is_active=True,
        deleted__isnull=True,
    ).order_by("order")
    serializer_class = serializers.CourseLessonTypeSerializer

    @swagger_auto_schema(tags=["course-admin"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


c_lesson_type_list_view = CourseLessonTypeListView.as_view()


class CategoryListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Category.api_objects.all_active().filter(
        parent__isnull=True).order_by("order")
    serializer_class = serializers.CategorySerializer

    @swagger_auto_schema(tags=["course-admin"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


category_list_view = CategoryListView.as_view()


class CreateCourseView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.CourseCreateSerializer

    @swagger_auto_schema(tags=["course-admin"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


course_create_view = CreateCourseView.as_view()


class CourseListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.CourseListSerializer
    queryset = Course.api_objects.all_active().order_by("order")

    @swagger_auto_schema(tags=["course-admin"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


admin_course_list_view = CourseListView.as_view()


class CourseRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = Course.objects.all()
    serializer_class = serializers.CourseCreateSerializer
    http_method_names = ['get', 'patch', 'delete']
    lookup_field = 'pk'

    @swagger_auto_schema(tags=["course-admin"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(tags=["course-admin"])
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=["course-admin"])
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.deleted = datetime.datetime.now()
        instance.save()


admin_course_retrieve_update_destroy_view = CourseRetrieveUpdateDestroyView.as_view()


class CreateTopicView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.TopicCreateSerializer

    @swagger_auto_schema(tags=["course-admin"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


topic_create_view = CreateTopicView.as_view()


class CourseTopicListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.CourseTopicListSerializer
    queryset = CourseTopic.api_objects.all_active().select_related(
        'topic'
    ).prefetch_related(
        'course_topic_lessons'
    ).order_by('order')
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.CourseTopicFilter

    @swagger_auto_schema(tags=["course-admin"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


admin_course_topic_list_view = CourseTopicListView.as_view()


class CourseTopicRetrieveUpdateDestroyView(
    generics.RetrieveUpdateDestroyAPIView
):
    permission_classes = [permissions.IsAuthenticated]
    queryset = CourseTopic.objects.all()
    serializer_class = serializers.CourseTopicCreateSerializer
    lookup_field = 'pk'

    @swagger_auto_schema(tags=["course-admin"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(tags=["course-admin"])
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=["course-admin"])
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.deleted = datetime.datetime.now()
        topic = instance.topic
        topic.deleted = datetime.datetime.now()
        topic.save()
        instance.save()


topic_retrieve_update_view = CourseTopicRetrieveUpdateDestroyView.as_view()


class CreateCLessonView(generics.CreateAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.CreateCLessonSerializer

    @swagger_auto_schema(tags=["course-admin"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


c_lesson_create_view = CreateCLessonView.as_view()


class RetrieveUpdateDestroyCLessonView(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = CLesson.objects.all()
    serializer_class = serializers.CreateCLessonSerializer
    lookup_field = 'pk'

    @swagger_auto_schema(tags=["course-admin"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(tags=["course-admin"])
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=["course-admin"])
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


retrieve_update_destroy_lesson_view = RetrieveUpdateDestroyCLessonView.as_view()


class CreateContentLessonView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.CreateContentLessonSerializer

    @swagger_auto_schema(tags=["course-admin"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


content_lesson_create_view = CreateContentLessonView.as_view()


class RetrieveUpdateDestroyContentLessonView(
    generics.RetrieveUpdateDestroyAPIView
):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.CreateContentLessonSerializer

    @swagger_auto_schema(tags=["course-admin"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


retrieve_update_destroy_content_lesson_view = RetrieveUpdateDestroyContentLessonView.as_view()
