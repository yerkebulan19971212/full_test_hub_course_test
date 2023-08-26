import requests
from django.db import transaction
from rest_framework.response import Response
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView

from src.common.models import QuizzType, CourseTypeQuizz
from src.common import filters, serializers


class GetAllActiveQuizzTypes(generics.ListAPIView):
    queryset = CourseTypeQuizz.objects.get_all_active()
    serializer_class = serializers.QuizzTypeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.QuizzTypeFilter


quizz_types_view = GetAllActiveQuizzTypes.as_view()
