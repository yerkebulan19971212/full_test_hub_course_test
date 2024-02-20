from django.db import transaction
from django.db.models import Max, Prefetch, Sum, Q, Count
from drf_writable_nested import WritableNestedModelSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
import django_filters

from django_filters import rest_framework as filters

from django_filters.rest_framework import DjangoFilterBackend
from src.accounts.api_views.serializers import StudentInformationUpdateSerializer, StudentDetailUpdateSerializer
from src.accounts.models import User
from src.common.models import CourseTypeLesson, Lesson, QuestionAnswerImage, CourseType
from src.common.paginations import SimplePagination, SimplePaginationV2
from src.quizzes.models import (Answer, CommonQuestion, Question,
                                QuestionLevel, Variant, LessonQuestionLevel)
from src.services.permissions import SuperAdminPermission
from src.services.utils import create_question


# --------------------------- serializers ------------------------------
class VariantListSerializer(serializers.ModelSerializer):
    variant = serializers.IntegerField(source='variant_title')
    name = serializers.CharField(source='name_code')
    test_lang = serializers.SerializerMethodField()
    sum_of_questions = serializers.IntegerField(default=120)

    class Meta:
        model = Variant
        fields = [
            'id',
            'name',
            'test_lang',
            'sum_of_questions',
            'variant',
            'is_active',
        ]

    def get_test_lang(self, obj):
        if obj.language == 'kz':
            return 0
        return 1


class LessonSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='name_kz')

    class Meta:
        model = Lesson
        fields = [
            'id',
            'icon',
            'choose_icon',
            'name',
        ]
        ref_name = "Lesson_1"


class VariantLessonSerializer(serializers.ModelSerializer):
    sum_of_question = serializers.IntegerField(default=0)
    number_of_questions = serializers.IntegerField(source='questions_number', default=40)
    lesson = LessonSerializer()

    class Meta:
        model = CourseTypeLesson
        fields = [
            'id',
            'lesson',
            'sum_of_question',
            'number_of_questions',
        ]


class CommonQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommonQuestion
        fields = (
            'id',
            'text',
            'file'
        )
        ref_name = "CommonQuestionSerializer"


class AnswerSerializer2(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Answer
        fields = [
            'id',
            'order',
            'answer',
            'correct'
        ]
        ref_name = "AnswerSerializer_2"


class AddCommonQuestionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='name_code')

    class Meta:
        model = CommonQuestion
        fields = (
            'id',
            'name',
            'text',
        )


class GetUpdateCommonQuestionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='name_code')

    class Meta:
        model = CommonQuestion
        fields = (
            'id',
            'name',
            'text',
        )


class ListCommonQuestionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='name_code')

    class Meta:
        model = CommonQuestion
        fields = (
            'id',
            'name'
        )


class SubQuestionListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        # Mapping of instance IDs to instance objects.
        sub_question_mapping = {sub_question.id: sub_question for sub_question
                                in instance}
        data_mapping = {item['id']: item for item in validated_data if
                        item.get('id')}

        # Perform creations and updates.
        ret = []
        for sub_question_id, data in data_mapping.items():
            sub_question = sub_question_mapping.get(sub_question_id, None)
            if sub_question is None:
                ret.append(self.child.create(data))
            else:
                ret.append(self.child.update(sub_question, data))

        # Perform deletions.
        for sub_question_id, sub_question in sub_question_mapping.items():
            if sub_question_id not in data_mapping:
                sub_question.delete()

        return ret


class ChildQuestionAdminSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer2(many=True)
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Question
        fields = (
            'id',
            'question',
            'answers'
        )
        list_serializer_class = SubQuestionListSerializer

    def update(self, instance, validated_data):
        # Update the sub-question instance
        instance.question = validated_data.get('question', instance.question)
        instance.save()

        # Update the nested answers
        answers_data = validated_data.get('answers')
        ansids = [i.id for i in Answer.objects.filter(question=instance)]
        old_ans_ids = []
        if answers_data is not None:
            for a in answers_data:
                ans_id = a.get("id")
                if ans_id:
                    old_ans_ids.append(ans_id)
                    qa = Answer.objects.get(pk=ans_id)
                    qa.answer = a.get("answer")
                    qa.order = a.get("order")
                    qa.correct = a.get("correct")
                    qa.save()
                else:
                    Answer.objects.create(
                        question=instance,
                        answer=a.get("answer"),
                        order=a.get("order"),
                        correct=a.get("correct"),
                    )
        delete_ids = []
        for i in ansids:
            if i not in old_ans_ids:
                delete_ids.append(i)
        Answer.objects.filter(id__in=delete_ids).delete()

        return instance

    def create(self, validated_data):
        question = Question.objects.create(
            parent=validated_data.get("parent"),
            question=validated_data.get("question"),
            variant=validated_data.get("variant"),
            lesson_question_level=validated_data.get("lesson_question_level"),
        )
        answers = []
        for a in validated_data.get("answers"):
            answers.append(
                Answer(
                    question=question,
                    answer=a.get("answer"),
                    order=a.get("order"),
                    correct=a.get("correct"),
                ))
        Answer.objects.bulk_create(answers)
        return question


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = (
            'id',
            'answer',
            'correct'
        )
        ref_name = "AnswerSerializer_1"


class QuestionAdminSerializer(serializers.ModelSerializer):
    number = serializers.IntegerField(default=0)
    answers = AnswerSerializer(many=True)
    common_question = CommonQuestionSerializer()
    question_level = serializers.CharField(source="lesson_question_level.question_level.name_code")
    sub_questions = ChildQuestionAdminSerializer(many=True)

    class Meta:
        model = Question
        fields = (
            'id',
            'number',
            'question_type',
            'question_level',
            'common_question',
            'question',
            'sub_questions',
            'answers'
        )


class QuestionLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionLevel
        fields = (
            'id',
            'name_code',
        )


class QuestionSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, required=True)
    sub_questions = ChildQuestionAdminSerializer(many=True, required=False)
    lesson = serializers.IntegerField(default=0, write_only=True)
    question_level = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = (
            'id',
            'variant',
            'lesson',
            'common_question',
            'question',
            'question_type',
            'sub_questions',
            'answers',
            'question_level',
            'answer_question',
            'answer_url',
            # 'number'
        )
        ref_name = "QuestionSerializer_1"

    def get_question_level(self, obj):
        # For retrieve action, return the ID of the question_level
        if self.context['request'].method == 'GET':
            return obj.lesson_question_level.question_level.id

    def update(self, instance, validated_data):
        lesson = validated_data.pop('lesson')
        question_level = self.context['request'].data.get('question_level', None)
        if question_level is not None:
            question_level_obj = LessonQuestionLevel.objects.filter(
                test_type_lesson=lesson,
                question_level_id=question_level
            )
            validated_data['lesson_question_level'] = question_level_obj.first()
        sub_questions_data = validated_data.pop('sub_questions', [])
        instance = super().update(instance, validated_data)
        questions = Question.objects.filter(
            parent=instance
        )
        if sub_questions_data:
            sub_questions_data_s = []
            sub_questions_data_c = []
            for q in sub_questions_data:
                idfg = q.get("id", None)
                if idfg:
                    sub_questions_data_s.append(q)
                else:
                    q["variant"] = validated_data.get("variant")
                    q["parent"] = instance
                    sub_questions_data_c.append(q)

            if sub_questions_data_s:
                self.fields['sub_questions'].update(questions,
                                                    sub_questions_data)
            else:
                self.fields['sub_questions'].create(sub_questions_data_c)
        else:
            Question.objects.filter(parent=instance).delete()

        return instance

    def create(self, validated_data):
        variant = validated_data.get('variant')
        lesson = validated_data.pop('lesson')
        question_level = validated_data.pop('question_level', None)
        lql_list = LessonQuestionLevel.objects.filter(test_type_lesson_id=lesson).order_by('id')
        if question_level:
            question_level_obj = LessonQuestionLevel.objects.filter(
                test_type_lesson=lesson,
                question_level_id=question_level
            )
            lql_list = [question_level_obj for i in range(len(lql_list))]
        sub_questions_data = validated_data.pop('sub_questions', [])
        question_count = Question.objects.filter(
            variant=variant,
            lesson_question_level__test_type_lesson_id=lesson
        ).count()
        index_lql = 0
        if question_count >= 0:
            index_lql = question_count // 5
        validated_data['lesson_question_level'] = lql_list[index_lql]
        question = super().create(validated_data)
        sub_questions_serializer = self.fields['sub_questions']
        for s in sub_questions_data:
            s["lesson_question_level"] = lql_list[index_lql]
            s["lesson"] = lesson
            s["variant"] = variant
            s["parent"] = question
        if sub_questions_data:
            sub_questions = sub_questions_serializer.create(sub_questions_data)
        return question


class CreateVariantJuz40Serializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    test_lang = serializers.IntegerField(write_only=True)
    name = serializers.CharField(write_only=True)

    class Meta:
        model = Variant
        fields = (
            'id',
            'test_lang',
            'name'
        )

    def create(self, validated_data):
        name = validated_data.pop('name', None)
        test_lang = validated_data.pop('test_lang', None)
        if test_lang == 0:
            validated_data['language'] = 'kz'
        else:
            validated_data['language'] = 'ru'

        course_type = CourseType.objects.all().first()
        validated_data['name_kz'] = name
        validated_data['name_ru'] = name
        validated_data['name_en'] = name
        validated_data['name_code'] = name
        validated_data['is_active'] = False
        validated_data['course_type'] = course_type
        variant = super().create(validated_data=validated_data)
        return variant


# --------------------------- views ------------------------------
class VariantView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, SuperAdminPermission]
    serializer_class = VariantListSerializer
    queryset = Variant.objects.all().order_by('-order')
    pagination_class = SimplePagination

    @swagger_auto_schema(tags=["super_admin"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


variant_list = VariantView.as_view()


class VariantLessonView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, SuperAdminPermission]
    serializer_class = VariantLessonSerializer
    queryset = CourseTypeLesson.objects.all().order_by('id')

    def get_queryset(self):
        queryset = super().get_queryset().annotate(
            sum_of_question=Count(
                'lesson_question_level__questions',
                filter=Q(
                    lesson_question_level__questions__parent__isnull=True,
                    lesson_question_level__questions__variant_id=self.kwargs['variant_id'],
                ),
                distinct=True
            ),
        )
        print(queryset.query)
        print("queryset.query")
        return queryset

    @swagger_auto_schema(tags=["super_admin"])
    def get(self, request, *args, **kwargs):
        variant_id = self.kwargs['variant_id']
        data = super().get(request, *args, **kwargs).data
        for d in data:
            d['variant_id'] = variant_id
        return Response(data)


variant_lesson_view = VariantLessonView.as_view()


class CheckAddQuestion(APIView):
    permission_classes = [permissions.IsAuthenticated, SuperAdminPermission]

    @swagger_auto_schema(tags=["super_admin"])
    def get(self, request, variant_id, lesson_id):
        add_question_status = True
        number = 0 + 1
        return Response({'status': add_question_status, 'number': number})


check_add_question_view = CheckAddQuestion.as_view()


class QuestionListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, SuperAdminPermission]
    serializer_class = QuestionAdminSerializer
    queryset = Question.objects.filter(parent__isnull=True).select_related(
        'lesson_question_level__question_level'
    ).order_by('id')

    def get_queryset(self):
        variant_id = self.kwargs['variant_id']
        lesson_id = self.kwargs['lesson_id']
        return super().get_queryset().filter(
            variant_id=variant_id,
            lesson_question_level__test_type_lesson_id=lesson_id
        )

    @swagger_auto_schema(tags=["super_admin"])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


question_list_view = QuestionListView.as_view()


class QuestionFilter(django_filters.FilterSet):
    question_level = filters.NumberFilter(
        field_name="lesson_question_level__question_level_id")

    class Meta:
        model = Question
        fields = (
            'question_level',
        )


class QuestionItemsListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, SuperAdminPermission]
    serializer_class = QuestionAdminSerializer
    queryset = Question.objects.filter(parent__isnull=True).select_related(
        'lesson_question_level__question_level'
    ).order_by('id')
    pagination_class = SimplePaginationV2
    filter_backends = [DjangoFilterBackend]
    filterset_class = QuestionFilter

    def get_queryset(self):
        variant_id = self.kwargs['variant_id']
        lesson_id = self.kwargs['lesson_id']
        return super().get_queryset().filter(
            variant_id=variant_id,
            lesson_question_level__test_type_lesson_id=lesson_id
        )

    @swagger_auto_schema(tags=["super_admin"])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


question_items_list_view = QuestionItemsListView.as_view()


class CommonQuestionListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, SuperAdminPermission]
    serializer_class = ListCommonQuestionSerializer
    queryset = CommonQuestion.objects.all().order_by('-id')

    @swagger_auto_schema(tags=["super_admin"])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


common_question_list_view = CommonQuestionListView.as_view()


class QuestionLevelListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, SuperAdminPermission]
    serializer_class = QuestionLevelSerializer
    queryset = QuestionLevel.objects.all().order_by('id')

    @swagger_auto_schema(tags=["super_admin"])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


question_level_list_view = QuestionLevelListView.as_view()


class ImportQuestionSerializer(serializers.Serializer):
    file = serializers.FileField()
    question_level = serializers.IntegerField(required=False)


class ImportQuestionsView(generics.CreateAPIView):
    # permission_classes = [permissions.IsAuthenticated, SuperAdminPermission]
    serializer_class = ImportQuestionSerializer

    @swagger_auto_schema(tags=["super_admin"])
    def post(self, request, *args, **kwargs):
        variant_id = self.kwargs['variant_id']
        lesson_id = self.kwargs['lesson_id']
        question_level = self.request.data.get('question_level', None)
        lql_list = LessonQuestionLevel.objects.filter(test_type_lesson_id=lesson_id).order_by('question_level__name_code')
        if question_level:
            if str(question_level).isnumeric():
                question_level_obj = LessonQuestionLevel.objects.filter(
                    test_type_lesson_id=lesson_id,
                    question_level_id=question_level
                )
                lql_list = [question_level_obj.first() for i in range(len(lql_list))]
        print(lql_list)
        print("lql_list")
        with request.FILES['file'] as f:
            try:
                with transaction.atomic():
                    line = f.readline().decode().strip()
                    questions_texts = ""
                    count = 0
                    while True:
                        if not line.strip():
                            index_lql = 0
                            if count >= 0:
                                index_lql = count // 5
                            count += 1
                            question = create_question(
                                questions_texts=questions_texts,
                                variant_id=variant_id,
                                lesson_id=lesson_id,
                                lql=lql_list[index_lql]
                            )
                            if question is None:
                                return Response(
                                    {"detail": "Что то не так"},
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                            questions_texts = ""
                        elif line == 'end' or line == 'End':
                            break
                        else:
                            questions_texts += line.strip() + "new_line"
                        line = f.readline().decode().strip()
            except Exception as e:
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response({"detail": "created"}, status=status.HTTP_201_CREATED)


import_question_view = ImportQuestionsView.as_view()


class AddQuestionView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, SuperAdminPermission]
    serializer_class = QuestionSerializer

    @swagger_auto_schema(tags=["super_admin"])
    def post(self, request, *args, **kwargs):
        answers = [ans for ans in self.request.data.get('answers') if
                   ans.get('answer')]
        request.data['answers'] = answers
        return self.create(request, *args, **kwargs)


add_question_view = AddQuestionView.as_view()


class GetUpdateDestroyQuestionView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, SuperAdminPermission]
    queryset = Question.objects.select_related(
        'common_question',
        'lesson_question_level__question_level',
    ).prefetch_related(
        'answers',
        Prefetch(
            'sub_questions',
            queryset=Question.objects.order_by('id'))
    ).all()
    serializer_class = QuestionSerializer
    lookup_field = 'pk'


get_update_destroy_question_view = GetUpdateDestroyQuestionView.as_view()


class QuestionAnswerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAnswerImage
        fields = (
            'upload',
        )


class SaveImageView(generics.CreateAPIView):
    serializer_class = QuestionAnswerImageSerializer

    def post(self, request, *args, **kwargs):
        data = self.create(request, *args, **kwargs).data
        return Response(
            data={"url": data.get('upload')},
            status=status.HTTP_201_CREATED
        )


save_image_view = SaveImageView.as_view()


class CreateVariantJuz40View(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, SuperAdminPermission]
    serializer_class = CreateVariantJuz40Serializer

    def perform_create(self, serializer):
        variant = Variant.objects.all().order_by('variant_title').last()
        order = Variant.objects.all().order_by('order').last()
        if variant is None:
            variant = 0
        else:
            variant = variant.variant_title
        serializer.save(
            variant_title=(variant + 1), order=(order.order + 1))


create_variant_view = CreateVariantJuz40View.as_view()


class StudentDetailView(generics.RetrieveDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated, SuperAdminPermission)
    serializer_class = StudentInformationUpdateSerializer
    queryset = User.objects.filter(role__name_code='student').order_by('id')
    lookup_field = 'pk'


student_detail = StudentDetailView.as_view()


class StudentDetailUpdateView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated, SuperAdminPermission)
    serializer_class = StudentDetailUpdateSerializer
    queryset = User.objects.filter(role__name_code='student')
    lookup_field = 'pk'
    http_method_names = ['patch']


student_detail_update = StudentDetailUpdateView.as_view()


class VariantDestroyJuz40View(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, SuperAdminPermission]
    queryset = Variant.objects.all()
    lookup_field = 'pk'

    def delete(self, request, *args, **kwargs):
        variant = self.get_object()
        if variant.is_active:
            return Response({"detail": 'Вы не можете удалить Варинт,'
                                       ' пока активно'})
        return self.destroy(request, *args, **kwargs)


destroy_variant = VariantDestroyJuz40View.as_view()


class AddCommonQuestion(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated, SuperAdminPermission,)
    serializer_class = AddCommonQuestionSerializer


add_common_question_view = AddCommonQuestion.as_view()


class GetUpdateCommonQuestionView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, SuperAdminPermission]
    queryset = CommonQuestion.objects.all()
    serializer_class = GetUpdateCommonQuestionSerializer
    lookup_field = 'pk'


get_update_common_view = GetUpdateCommonQuestionView.as_view()
