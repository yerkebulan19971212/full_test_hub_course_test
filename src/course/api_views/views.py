import uuid

from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions

from src.course import serializers
from src.course.models import Course, CourseTopic, CLesson, Topic
from src.course.serializers.course import CourseCurriculumFilterSerializer


class CourseListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Course.api_objects.first_page()
    serializer_class = serializers.CourseSerializer

    @swagger_auto_schema(tags=["course"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


course_list_view = CourseListView.as_view()


class CourseRetrieveView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Course.api_objects.is_active().select_related('owner')
    serializer_class = serializers.CourseOneSerializer
    lookup_field = 'uuid'

    @swagger_auto_schema(tags=["course"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


course_view = CourseRetrieveView.as_view()


class CourseCurriculumView(generics.ListAPIView):
    queryset = CourseTopic.objects.prefetch_related(
        'course_topic_lessons__course_lesson'
    )
    serializer_class = serializers.CourseTopicCurriculumSerializer

    def get_queryset(self):
        uuid = self.request.query_params.get('uuid')
        queryset = super().get_queryset().filter(
            course__uuid=uuid).prefetch_related(
            'course_topic_lessons'
        )
        return queryset

    @swagger_auto_schema(tags=["course"],
                         query_serializer=CourseCurriculumFilterSerializer)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


course_curriculum_view = CourseCurriculumView.as_view()


class CourseCurriculumUserView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Topic.objects.all()
    serializer_class = serializers.CourseCurriculumUserSerializer

    def get_queryset(self):
        uuid = self.request.query_params.get('uuid')
        queryset = super().get_queryset().filter(
            course_topic__course__uuid=uuid)
        return queryset

    @swagger_auto_schema(tags=["course"],
                         query_serializer=CourseCurriculumFilterSerializer)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


course_curriculum_user_view = CourseCurriculumUserView.as_view()


class CourseLessonUserView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = CLesson.objects.all()
    serializer_class = serializers.CourseLessonUserSerializer

    def get_queryset(self):
        uuid = self.request.query_params.get('uuid')
        return super().get_queryset().filter(
            course_topic_lessons__course_topic__topic__uuid=uuid
        )

    @swagger_auto_schema(tags=["course"],
                         query_serializer=CourseCurriculumFilterSerializer)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


course_lesson_user_view = CourseLessonUserView.as_view()


class CourseLessonUserView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = CLesson.objects.all()
    serializer_class = serializers.CourseLessonUserSerializer

    def get_queryset(self):
        uuid = self.request.query_params.get('uuid')
        return super().get_queryset().filter(
            course_topic_lessons__course_topic__topic__uuid=uuid
        )

    @swagger_auto_schema(tags=["course"],
                         query_serializer=CourseCurriculumFilterSerializer)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


course_lesson_user_view = CourseLessonUserView.as_view()
