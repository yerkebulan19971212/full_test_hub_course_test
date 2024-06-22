import requests
from django.db import transaction
from django.db.models import Exists, OuterRef
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView

from src.common.constant import QuestionType
from src.common.models import Lesson, CourseTypeLesson, CourseType, LessonPair
from src.common.serializers import LessonSerializer, LessonPairListSerializer, \
    LessonWithPairsSerializer
from src.common import filters
from src.quizzes.models import QuestionLevel, LessonQuestionLevel, \
    CommonQuestion, Question, Answer, VariantQuestion, Variant, AnswerSign
from src.quizzes.serializers import ImportQuestionQuerySerializer


class GetAllActiveLesson(generics.ListAPIView):
    queryset = Lesson.objects.get_all_active()
    serializer_class = LessonSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.LessonFilter

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


get_all_active_lesson_view = GetAllActiveLesson.as_view()


class ImportQuestionFromTestHubApp(APIView):
    # queryset = Lesson.objects.get_all_active()
    # serializer_class = LessonSerializer
    # filter_backends = [DjangoFilterBackend]
    # filterset_class = filters.LessonFilter
    @swagger_auto_schema(tags=["import"],
                         query_serializer=ImportQuestionQuerySerializer)
    def get(self, request, *args, **kwargs):
        questions_objects = {}
        variant_id = self.request.query_params.get("variant_id")
        lessons = Lesson.objects.get_all_active()
        variant_list_url = f"http://127.0.0.1:8003/api/v1/super-admin/variant-list/"
        res = requests.get(variant_list_url)
        answersign = AnswerSign.objects.all()
        print(res)
        print("=======res")
        ql_list = QuestionLevel.objects.all().order_by('id')
        # try:
        print(res.json())
        print('sss')
        with transaction.atomic():

            for v in res.json():
                print('===============================================')
                question_l = []
                variant = Variant.objects.create(
                    course_type=CourseType.objects.all().first(),
                    variant_title=v["variant"],
                    name_ru=v["variant"],
                    name_kz=v["variant"],
                    name_en=v["variant"],
                    name_code=v["variant"],
                )
                print(variant)
                print("variant")
                for l in lessons:
                    question_url = "http://127.0.0.1:8003/api/v1/quizzes/get-all-question-2-2/?"
                    question_url += "variant_id=" + str(
                        v.get('id')) + "&lesson_code=" + l.name_code
                    res_q = requests.get(question_url)

                    start = 0
                    end = 16
                    if l.name_code == 'tgo':
                        end = 15
                    order = 1

                    for ql in ql_list:
                        for r in res_q.json()[start:end]:
                            question = r
                            comon_q = question["common_question"]
                            common_q_o = None
                            if comon_q:
                                common_q_o, _ = CommonQuestion.objects.get_or_create(
                                    name_code=comon_q["name"],
                                    text=comon_q["text"],
                                )
                                if comon_q['file']:
                                    common_q_o.file.name = comon_q["file"].split('media')[1]
                            lq = LessonQuestionLevel.objects.filter(
                                question_level=ql,
                                test_type_lesson__lesson=l
                            ).first()
                            question_type = QuestionType.DEFAULT
                            if question["question_type"] == "SELECT":
                                question_type = QuestionType.SELECT
                            q = Question.objects.create(
                                order=order,
                                question_type=question_type,
                                lesson_question_level=lq,
                                common_question=common_q_o,
                                question=question["question"],
                                variant=variant,
                                parent_id=questions_objects.get(
                                    question["parent"], None)
                            )
                            questions_objects[question["id"]] = q.id
                            if question_type == QuestionType.SELECT:
                                parent_url = f"http://127.0.0.1:8003/api/v1/quizzes/get-all-question-parent/?parent={question['id']}"
                                res_q_p = requests.get(parent_url)
                                for r in res_q_p.json():
                                    question = r
                                    qp = Question.objects.create(
                                        order=order,
                                        question_type=question_type,
                                        lesson_question_level=lq,
                                        common_question=common_q_o,
                                        question=question["question"],
                                        variant=variant,
                                        parent_id=q.id
                                    )
                                    Answer.objects.bulk_create([
                                        Answer(
                                            answer_sign=answersign[i],
                                            question=qp,
                                            answer=a["answer"],
                                            correct=a["correct"],
                                            order=a["order"],
                                        ) for i, a in
                                        enumerate(question["answer"])
                                    ])
                            elif question_type == QuestionType.DEFAULT:
                                Answer.objects.bulk_create([
                                    Answer(
                                        answer_sign=answersign[i],
                                        question=q,
                                        answer=a["answer"],
                                        correct=a["correct"],
                                        order=a["order"]
                                    ) for i, a in enumerate(question["answer"])
                                ])
                            question_l.append(VariantQuestion(
                                variant=variant,
                                question=q
                            ))

                            order += 1

                        start = end
                        if l.name_code == 'eng' and ql.name_code == "A":
                            end += 18
                        elif l.name_code == 'eng' and ql.name_code != "A":
                            end += 16
                        if l.name_code == 'tgo' and ql.name_code == "A":
                            end += 15
                VariantQuestion.objects.bulk_create(question_l)
        # except Exception as e:
        #     print(e)
        #     return Response(str(e))
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
