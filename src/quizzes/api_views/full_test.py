from datetime import datetime

from django.db.models import Sum
from django.db.models.functions import Coalesce
from rest_framework import generics, status
from rest_framework import permissions
from rest_framework import views
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from src.common.models import Lesson
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


class ENTLessonListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ENTLessonListSerializer
    queryset = Lesson.objects.all()

    def get(self, request, *args, **kwargs):
        student_id = self.kwargs.get('test_id')
        student_test = get_object_or_404(
            StudentQuizz.objects.select_related(
                'variant'
            ),
            pk=student_id)

        if (student_test.status != "NOT_PASSED"
                and student_test.status != "CONTINUE"):
            return Response({"detail": "Вы уже прошли этот тест"},
                            status=status.HTTP_400_BAD_REQUEST)
        elif datetime.now() > localtime(student_test.end_time).replace(
                tzinfo=None):
            return Response({"detail": "Тест тапсыратын уакыт отип кетти"},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            student_test.status = "CONTINUE"

            student_test.save()
        duration_time = {
            "hour": 0,
            "minute": 0,
            "seconds": 0
        }
        if not student_test.test_start_time:
            student_test.test_start_time = datetime.now()
            student_test.save()
            difference_duration = timedelta(seconds=0)
        else:
            test_start_time = student_test.test_start_time
            difference_duration = datetime.now() - localtime(
                test_start_time).replace(tzinfo=None)
        duration = student_test.variant.duration
        if difference_duration <= duration:
            duration = student_test.variant.duration - difference_duration
            duration_time = {
                "hour": duration.seconds // 3600,
                "minute": (duration.seconds // 60) % 60,
                "seconds": duration.seconds % 60
            }
        data = self.list(request, *args, **kwargs).data

        return Response({
            "lessons": data,
            "duration": duration_time
        }, status=status.HTTP_200_OK)

    def get_queryset(self):
        student_test_id = self.kwargs.get('test_id')
        student_test = get_object_or_404(
            StudentQuizz.objects.select_related(
            'variant',
            'lessons',
            'lessons__lesson_2',
            'lessons__lesson_1',
        ), pk=student_test_id)

        queryset = self.queryset
        main_lessons = queryset.filter(
            test_type_lessons__type__name="ent",
            test_type_lessons__main=True,
        ).order_by('test_type_lessons__main', 'id')
        if student_test.lessons.lesson_1.name_ru == "Творческий экзамен":
            main_lessons = main_lessons.exclude(
                name_ru="Математическая грамотность")
        if student_test.lessons and not student_test.lessons.lesson_1.name_ru == "Творческий экзамен":
            other_lessons = queryset.filter(
                test_type_lessons__type__name="ent",
                id__in=[student_test.lessons.lesson_1_id,
                        student_test.lessons.lesson_2_id])
            main_lessons = main_lessons | other_lessons
        main_lessons = main_lessons.annotate(
            sum_of_questions=Count('variant_lessons__questions',
                                   filter=Q(
                                       variant_lessons__variant=student_test.variant))
        )

        return main_lessons.order_by('test_type_lessons__type', 'id')
