from django.db.models import Count
from django.shortcuts import render
from config.celery import student_user_question_count

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from src.common.constant import QuizzStatus
from src.common.models import CourseTypeLesson
from src.quizzes.models import Question, Answer, QuestionLevel, \
    LessonQuestionLevel, TestFullScore, Variant, CommonQuestion


class UtilsView(APIView):
    def get(self, request, *args, **kwargs):
        student_user_question_count.delay(19, [39489], 4)
        return Response("")


utils_v = UtilsView.as_view()
