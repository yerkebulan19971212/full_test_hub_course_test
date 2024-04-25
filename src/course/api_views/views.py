import uuid

from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions
from rest_framework.response import Response

from src.common.exception import BuyCourseException
from src.course import serializers
from src.course.models import Course, CourseTopic, CLesson, Topic, \
    CourseTopicLesson
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
    permission_classes = [permissions.IsAuthenticated]
    queryset = CourseTopic.api_objects.all_active()
    serializer_class = serializers.CourseTopicCurriculumSerializer

    def get_queryset(self):
        uuid = self.request.query_params.get('uuid')
        course_topic_lessons = CourseTopicLesson.objects.all().order_by(
            'course_lesson__order')
        return super().get_queryset().filter(
            course__uuid=uuid
        ).prefetch_related(
            Prefetch('course_topic_lessons', queryset=course_topic_lessons)
        )

    @swagger_auto_schema(tags=["course"],
                         query_serializer=CourseCurriculumFilterSerializer)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


course_curriculum_view = CourseCurriculumView.as_view()


class CourseCurriculumUserView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = CourseTopic.objects.all()
    serializer_class = serializers.CourseCurriculumUserSerializer

    def get_queryset(self):
        uuid = self.request.query_params.get('uuid')
        user = self.request.user
        queryset = super().get_queryset().filter(
            course__uuid=uuid,
            course__user_courses__user=user
        )
        if not queryset.exists():
            raise BuyCourseException()
        return queryset

    @swagger_auto_schema(tags=["course"],
                         query_serializer=CourseCurriculumFilterSerializer)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


course_curriculum_user_view = CourseCurriculumUserView.as_view()


# class CourseLessonUserView(generics.ListAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     queryset = CLesson.objects.all()
#     serializer_class = serializers.CourseLessonUserSerializer
#
#     def get_queryset(self):
#         uuid = self.request.query_params.get('uuid')
#         return super().get_queryset().filter(
#             course_topic_lessons__course_topic__topic__uuid=uuid
#         )
#
#     @swagger_auto_schema(tags=["course"],
#                          query_serializer=CourseCurriculumFilterSerializer)
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#
# course_lesson_user_view = CourseLessonUserView.as_view()
#

class CourseLessonUserView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = CLesson.objects.all()
    serializer_class = serializers.CourseLessonUserSerializer
    lookup_field = 'uuid'

    @swagger_auto_schema(tags=["course"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


course_lesson_user_view = CourseLessonUserView.as_view()


class BuyCourse(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.BuyCourseSerializer

    @swagger_auto_schema(tags=["course"])
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


buy_course_view = BuyCourse.as_view()


class CheckBuyCourse(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Course.objects.all()
    serializer_class = serializers.BuyCourseSerializer
    lookup_field = 'uuid'

    @swagger_auto_schema(tags=["course"])
    def get(self, request, *args, **kwargs):
        uuid = self.kwargs['uuid']
        user = self.request.user
        queryset = super().get_queryset().filter(
            uuid=uuid,
            user_courses__user=user
        )
        if queryset.exists():
            return Response({"status": True})
        return Response({"status": False})


check_buy_course_view = CheckBuyCourse.as_view()


class HasCourseView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Course.objects.all()
    serializer_class = serializers.BuyCourseSerializer
    lookup_field = 'uuid'

    @swagger_auto_schema(tags=["course"])
    def get(self, request, *args, **kwargs):
        uuid = self.kwargs['uuid']
        queryset = super().get_queryset().filter(
            uuid=uuid,
        )
        if queryset.exists():
            return Response({"status": True})
        return Response({"status": False})


has_course_view = HasCourseView.as_view()
