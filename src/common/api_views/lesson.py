from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend

from src.common.models import Lesson
from src.common.serializers import LessonSerializer
from src.common import filters


class GetAllActiveLesson(generics.ListAPIView):
    queryset = Lesson.objects.get_all_active()
    serializer_class = LessonSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.LessonFilter


get_all_active_lesson_view = GetAllActiveLesson.as_view()
