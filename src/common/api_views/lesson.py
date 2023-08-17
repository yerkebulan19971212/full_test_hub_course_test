from rest_framework import generics

from src.common.models import Lesson
from src.common.serializers import LessonSerializer


class GetAllActiveLessonByCourseType(generics.ListAPIView):
    queryset = Lesson.objects.filter(is_active=True)
    serializer_class = LessonSerializer



get_all_active_lesson_by_course_type_view = GetAllActiveLessonByCourseType.as_view()