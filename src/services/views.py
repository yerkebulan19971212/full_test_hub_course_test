from django.db.models import Count
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from src.common.constant import QuizzStatus
from src.common.models import CourseTypeLesson
from src.quizzes.models import Question, Answer, QuestionLevel, \
    LessonQuestionLevel, TestFullScore


class UtilsView(APIView):
    def get(self, request, *args, **kwargs):
        # t = TestFullScore.objects.values(
        #     "student_quizz", "lesson", "score"
        # ).annotate(scdf=Count("id")).filter(
        #     scdf__gt=1
        # )
        # for b in t:
        #     print(b.get("student_quizz"), " - ", b.get("lesson"), " - ",
        #           b.get("score"), " - ", b.get("scdf"))
        #     print("======")
        #     cc = TestFullScore.objects.filter(
        #         student_quizz_id=b.get("student_quizz"),
        #         lesson_id=b.get("lesson"),
        #         score=b.get("score"),
        #     )
        #     for c in range(len(cc)-1):
        #         print(cc[c].id)
        #         print("cc[c]")
        #         TestFullScore.objects.filter(
        #             pk=cc[c].pk
        #         ).delete()

        from src.services.utils import finish_full_test
        from src.quizzes.models import (StudentQuizz)
        student_quizzes = StudentQuizz.objects.filter(
            status=QuizzStatus.PASSED,
        )
        for s in student_quizzes:
            finish_full_test(student_quizz_id=s.id)
        return Response("")


utils_v = UtilsView.as_view()
