from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions

from src.course import serializers
from src.course.models import Course, CourseTopic, CLesson
from src.course.serializers.course import CourseCurriculumFilterSerializer


class CourseListView(generics.ListAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = Course.api_objects.first_page()
    serializer_class = serializers.CourseSerializer

    @swagger_auto_schema(tags=["course"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


course_list_view = CourseListView.as_view()


class CourseRetrieveView(generics.RetrieveAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = Course.api_objects.is_active()
    serializer_class = serializers.CourseSerializer
    lookup_field = 'uuid'

    @swagger_auto_schema(tags=["course"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


course_view = CourseRetrieveView.as_view()


class CourseCurriculumView(generics.ListAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = CourseTopic.objects.all().filter().prefetch_related(
    )
    serializer_class = serializers.CourseCurriculumSerializer
    lookup_field = 'uuid'

    def get_queryset(self):
        uuid = self.request.query_params.get('uuid')
        course_lesson = CLesson.objects.filter(
            course_topic_lessons__course_topic__course__uuid=uuid,
        )
        queryset = super().get_queryset().prefetch_related(
            Prefetch('course_topic_lessons__course_lesson', queryset=course_lesson),
        )
        return queryset

    @swagger_auto_schema(tags=["course"],
                         query_serializer=CourseCurriculumFilterSerializer)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


course_curriculum_view = CourseCurriculumView.as_view()
