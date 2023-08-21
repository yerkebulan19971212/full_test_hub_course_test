from datetime import datetime

from django.db.models import Sum
from django.db.models.functions import Coalesce
from rest_framework import generics, status
from rest_framework import permissions
from rest_framework import views
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from src.quizzes.models import Question, Answer, StudentScore
from src.quizzes import serializers
from src.quizzes import filters
from src.quizzes.models.student_quizz import StudentQuizzQuestion, StudentQuizz


class NewFullTest(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.FullQuizzSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(tags=["full-test"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


new_full_test_view = NewFullTest.as_view()


class StudentQuizzInformationView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.StudentQuizzInformationSerializer
    queryset = StudentQuizz.objects.select_related().all()
    lookup_field = 'pk'

    # # def get_queryset(self):
    # #     pk = self.kwargs.get('pk')
    # #     user = self.request.user
    # #     test_type = self.kwargs.get('test_type')
    # #     queryset = self.queryset.filter(
    # #         pk=pk,
    # #         user=user,
    #         variant__variant_lessons__lesson__test_type_lessons__type__name=test_type
    #     # )
    #     student_test = queryset.first()
    #     test_start_time = student_test.test_start_time
    #     duration = student_test.variant.duration
    #     difference_duration = datetime.now() - localtime(
    #         test_start_time).replace(tzinfo=None)
    #     if duration < difference_duration:
    #         finish_ent(student_test)
    #     # return queryset.all()


full_quizz_view = StudentQuizzInformationView.as_view()
