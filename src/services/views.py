from django.db.models import Count
from django.shortcuts import render
from config.celery import student_user_question_count

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from src.accounts.models import User
from src.common.constant import QuizzStatus
from src.common.models import CourseTypeLesson
from src.quizzes.models import Question, Answer, QuestionLevel, \
    LessonQuestionLevel, TestFullScore, Variant, CommonQuestion, StudentQuizz


class UtilsView(APIView):
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        for u in users:
            student_quizzes = StudentQuizz.objects.filter(user=u)
            for s in student_quizzes:
                questions = Question.objects.filter(
                    student_quizz_questions__student_quizz=s
                )
                question_ids = [q.id for q in questions]
                student_user_question_count.delay(u.id, question_ids, s.quizz_type.id)
        return Response("")


utils_v = UtilsView.as_view()
