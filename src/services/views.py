from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from src.common.models import CourseTypeLesson
from src.quizzes.models import Question, Answer, QuestionLevel, \
    LessonQuestionLevel


class UtilsView(APIView):
    def get(self, request, *args, **kwargs):
        return Response("")


utils_v = UtilsView.as_view()
