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
        # print('====++++++===')
        # a = QuestionLevel.objects.filter(name_code='A').first()
        # b = QuestionLevel.objects.filter(name_code='B').first()
        # c = QuestionLevel.objects.filter(name_code='C').first()
        # d = QuestionLevel.objects.filter(name_code='D').first()
        # e = QuestionLevel.objects.filter(name_code='E').first()
        # f = QuestionLevel.objects.filter(name_code='F').first()
        # g = QuestionLevel.objects.filter(name_code='G').first()
        # h = QuestionLevel.objects.filter(name_code='H').first()
        # for v in [76, 77, 78]:
        #     cs = CourseTypeLesson.objects.filter(main=False)
        #     for df in cs:
        #         questions = list(
        #             Question.objects.filter(
        #                 variant_id=v,
        #                 lesson_question_level__test_type_lesson=df
        #             ).order_by('id')
        #         )
        #         print('======-==-=-')
        #         for i,q in enumerate(questions):
        #             lql = q.lesson_question_level
        #             lesson = lql.test_type_lesson
        #             ql = lql.question_level
        #             if q.common_question is not None:
        #                 print(f'common-questions {lesson.id}')
        #                 lql_o = LessonQuestionLevel.objects.filter(
        #                     question_level=f,
        #                     test_type_lesson=lesson
        #                 ).first()
        #                 q.lesson_question_level = lql_o
        #                 q.save()
        #                 continue
        #             answer_count = Answer.objects.filter(question=q).count()
        #             if answer_count == 6:
        #                 print('answer-count')
        #                 lql_o = LessonQuestionLevel.objects.filter(
        #                     question_level=h,
        #                     test_type_lesson=lesson
        #                 ).first()
        #                 q.lesson_question_level = lql_o
        #                 q.save()
        #                 continue
        #             print('==========')
        #             print(i)
        #             question_level = a
        #             if i>4:
        #                 question_level = b
        #             if i>9:
        #                 question_level = c
        #             if i>14:
        #                 question_level = d
        #             if i>19:
        #                 question_level = e
        #             print(question_level)
        #             print("question_level")
        #             lql_o = LessonQuestionLevel.objects.filter(
        #                 question_level=question_level,
        #                 test_type_lesson=lesson
        #             ).first()
        #             q.lesson_question_level = lql_o
        #             q.save()
        return Response("")


utils_v = UtilsView.as_view()
