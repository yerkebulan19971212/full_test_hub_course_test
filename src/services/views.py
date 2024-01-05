from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from src.quizzes.models import Question, Answer


class UtilsView(APIView):
    def get(self, request, *args, **kwargs):
        questions = Question.objects.filter(parent__isnull=False)
        for q in questions:
            q2_list = Answer.objects.filter(question=q)
            for i, q2 in enumerate(q2_list):
                q2.order = i + 1
                q2.save()
        return Response("")


utils_v = UtilsView.as_view()
