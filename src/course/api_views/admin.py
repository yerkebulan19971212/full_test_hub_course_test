import datetime

from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.views import APIView

from src.course.models import (Category, Course, CourseTopic, CourseLessonType,
                               CLesson)
from src.course import serializers, filters
from src.course.models.c_lesson import CLessonContent, CourseTopicLesson
from src.course.serializers.admin import OrderUpdateSerializer


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
    permission_classes = [permissions.IsAuthenticated]
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
    ).order_by('order')
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.CourseTopicFilter

    def get_queryset(self):
        course_topic_lessons = CourseTopicLesson.objects.all().order_by(
            'course_lesson__order')
        return super().get_queryset().prefetch_related(
            Prefetch('course_topic_lessons', queryset=course_topic_lessons))

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
    queryset = CLessonContent.objects.all()
    serializer_class = serializers.CreateContentLessonSerializer

    @swagger_auto_schema(tags=["course-admin"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(tags=["course-admin"])
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=["course-admin"])
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


retrieve_update_destroy_content_lesson_view = RetrieveUpdateDestroyContentLessonView.as_view()


class ContentCLessonOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        tags=["course-admin"],
        request_body=OrderUpdateSerializer()
    )
    def post(self, request, *args, **kwargs):
        content_data = request.data
        model = CLessonContent
        if content_data.get("name") == 'CONTENT':
            model = CLessonContent
        elif content_data.get("name") == 'LESSON':
            model = CLesson
        elif content_data.get("name") == 'TOPIC':
            model = CourseTopic
        for o in content_data.get("order_list"):
            model.objects.filter(id=o.get('id')).update(**{
                'order': o.get("order")
            })

        return Response({"success": True}, status=status.HTTP_200_OK)


order_view = ContentCLessonOrderView.as_view()
