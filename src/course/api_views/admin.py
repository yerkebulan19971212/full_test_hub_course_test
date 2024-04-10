import datetime

from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions

from src.course.models import Category, Course
from src.course import serializers


class CategoryListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Category.api_objects.all_active()
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
    queryset = Course.api_objects.all_active()

    @swagger_auto_schema(tags=["course-admin"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


admin_course_list_view = CourseListView.as_view()


class CourseRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Course.objects.all()
    serializer_class = serializers.CourseCreateSerializer
    http_method_names = ['get', 'patch', 'delete']
    lookup_field = 'uuid'

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
