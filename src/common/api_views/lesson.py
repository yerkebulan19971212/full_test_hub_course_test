import requests
from django.db import transaction
from django.db.models import Exists, OuterRef
from rest_framework.response import Response
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView

from src.common.models import Lesson, CourseTypeLesson, CourseType, LessonPair
from src.common.serializers import LessonSerializer, LessonPairListSerializer, \
    LessonWithPairsSerializer
from src.common import filters
from src.quizzes.models import QuestionLevel, LessonQuestionLevel, \
    CommonQuestion, Question, Answer, VariantQuestion, Variant


class GetAllActiveLesson(generics.ListAPIView):
    queryset = Lesson.objects.get_all_active()
    serializer_class = LessonSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.LessonFilter

    def get(self, request, *args, **kwargs):
        # lessons = Lesson.objects.get_all_active()
        # course_type = CourseType.objects.all().first()
        # df = []
        # for l in lessons:
        #     df.append(CourseTypeLesson(
        #         course_type=course_type,lesson=l,questions_number=35,order=0,
        #     ))
        # CourseTypeLesson.objects.bulk_create(df)
        # lessons = CourseTypeLesson.objects.all()
        # q = QuestionLevel.objects.all()
        # dfg = []
        # for l in lessons:
        #     for r in q:
        #         dfg.append(LessonQuestionLevel(
        #             order=r.order,
        #             is_active=True,
        #             test_type_lesson=l,
        #             question_level=r
        #         ))
        # LessonQuestionLevel.objects.bulk_create(dfg)
        return self.list(request, *args, **kwargs)


get_all_active_lesson_view = GetAllActiveLesson.as_view()


class ImportQuestionFromTestHubApp(APIView):
    # queryset = Lesson.objects.get_all_active()
    # serializer_class = LessonSerializer
    # filter_backends = [DjangoFilterBackend]
    # filterset_class = filters.LessonFilter

    def get(self, request, *args, **kwargs):
        lessons = Lesson.objects.get_all_active()
        variant_list_url = "http://127.0.0.1:8008/api/v1/generation/variant-list/"
        res = requests.get(variant_list_url)
        try:
            with transaction.atomic():
                for v in res.json():
                    print('===============================================')
                    question_l = []
                    variant = Variant.objects.create(
                        course_type=CourseType.objects.all().first(),
                        variant_title=v["variant"]
                    )
                    for l in lessons:
                        question_url = "http://127.0.0.1:8008/api/v1/generation/variant-question-list/?"
                        question_url += "variant_id=" + str(
                            v.get('id')) + "&lesson_code=" + l.name_code
                        print(question_url)
                        res_q = requests.get(question_url)
                        for r in res_q.json():
                            question = r["question"]
                            comon_q = question["common_question"]
                            common_q_o = None
                            if comon_q:
                                common_q_o, _ = CommonQuestion.objects.get_or_create(
                                    # name_code=comon_q["name_code"],
                                    file=comon_q["file"],
                                    text=comon_q["text"],
                                )
                            lq = LessonQuestionLevel.objects.filter(
                                question_level__name_code=
                                question["lesson_question_level"]["name_code"],
                                test_type_lesson__lesson=l
                            ).first()
                            q = Question.objects.create(
                                lesson_question_level=lq,
                                common_question=common_q_o,
                                question=question["question"],
                                math=question["math"],
                                variant=variant
                            )
                            Answer.objects.bulk_create([
                                Answer(
                                    question=q,
                                    answer=a["answer"],
                                    correct=a["correct"],
                                    math=a["math"],
                                    answer_sign_id=a["answer_sign"],
                                ) for a in question["answers"]
                            ])
                            question_l.append(VariantQuestion(
                                variant=variant,
                                question=q
                            ))
                    VariantQuestion.objects.bulk_create(question_l)
        except Exception as e:
            print(e)
            return Response(str(e))
        return Response(res.json())


import_question_from_test_hub_app = ImportQuestionFromTestHubApp.as_view()


class LessonPairListView(generics.ListAPIView):
    serializer_class = LessonPairListSerializer
    queryset = LessonPair.objects.only(
        'id', 'lesson_1', 'lesson_2'
    ).select_related(
        'lesson_1', 'lesson_2'
    ).all()


lesson_pair_list_view = LessonPairListView.as_view()


class GetAllActiveLessonWithPairs(generics.ListAPIView):
    queryset = Lesson.objects.get_all_active().annotate(
        main=Exists(
            CourseTypeLesson.objects.filter(
                lesson_id=OuterRef('pk'),
                main=True
            ))
    ).order_by('-main')
    serializer_class = LessonWithPairsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.LessonFilter

    def get(self, request, *args, **kwargs):
        # lessons = Lesson.objects.get_all_active()
        # course_type = CourseType.objects.all().first()
        # df = []
        # for l in lessons:
        #     df.append(CourseTypeLesson(
        #         course_type=course_type,lesson=l,questions_number=35,order=0,
        #     ))
        # CourseTypeLesson.objects.bulk_create(df)
        # lessons = CourseTypeLesson.objects.all()
        # q = QuestionLevel.objects.all()
        # dfg = []
        # for l in lessons:
        #     for r in q:
        #         dfg.append(LessonQuestionLevel(
        #             order=r.order,
        #             is_active=True,
        #             test_type_lesson=l,
        #             question_level=r
        #         ))
        # LessonQuestionLevel.objects.bulk_create(dfg)
        return self.list(request, *args, **kwargs)


get_all_active_lesson_with_pairs_view = GetAllActiveLessonWithPairs.as_view()
