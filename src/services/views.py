from django.db.models import Count
from django.shortcuts import render
from config.celery import add_balance_to_student

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from src.common.constant import QuizzStatus
from src.common.models import CourseTypeLesson
from src.quizzes.models import Question, Answer, QuestionLevel, \
    LessonQuestionLevel, TestFullScore, Variant, CommonQuestion


class UtilsView(APIView):
    def get(self, request, *args, **kwargs):
        add_balance_to_student.delay()
        return Response("")


utils_v = UtilsView.as_view()
