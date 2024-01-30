from django.db import transaction
from django.db.models import Max
from drf_writable_nested import WritableNestedModelSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, serializers, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from src.common.models import CourseTypeLesson, Lesson
from src.common.paginations import SimplePagination
from src.quizzes.models import Variant, Question, CommonQuestion, Answer
from src.quizzes.serializers import AnswerSerializer
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
    sum_of_question = serializers.IntegerField(default=40)
    number_of_questions = serializers.IntegerField(default=0)
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


class AnswerSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = [
            'id',
            'order',
            'answer',
            'correct'
        ]
        ref_name = "AnswerSerializer_2"


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
            variant_lesson=validated_data.get("variant_lesson"),
        )
        answers = []
        for a in validated_data.get("answers"):
            print(a)
            print(a.get("order"))
            print('a.get("order")')
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
    sub_questions = ChildQuestionAdminSerializer(many=True)

    class Meta:
        model = Question
        fields = (
            'id',
            'number',
            'question_type',
            # 'variant_lesson',
            'common_question',
            'question',
            'sub_questions',
            'answers'
        )


class QuestionSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, required=True)
    sub_questions = ChildQuestionAdminSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = (
            'id',
            # 'variant_lesson',
            'common_question',
            'question',
            'question_type',
            'sub_questions',
            'answers',
            # 'number'
        )
        ref_name = "QuestionSerializer_1"

    def update(self, instance, validated_data):
        sub_questions_data = validated_data.pop('sub_questions', [])
        print(sub_questions_data)
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
                    q["variant_lesson"] = validated_data.get("variant_lesson")
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
        variant_lesson = validated_data.get('variant_lesson')
        sub_questions_data = validated_data.pop('sub_questions', [])
        answers = validated_data.get('answers')
        quantity_correct = 0
        for i in answers:
            if i.get('correct'):
                quantity_correct += 1
        validated_data['quantity_correct_answers'] = quantity_correct

        if len(answers) > 5:
            validated_data['choice_type'] = 'MULTICHOICE'
            validated_data['point'] = 2

        number__max = Question.objects.filter(
            variant_lesson_id=validated_data.get('variant_lesson')
        ).aggregate(Max('number'))['number__max']
        if number__max is None:
            number__max = 0
        validated_data['number'] = number__max + 1
        question = super().create(validated_data)
        sub_questions_serializer = self.fields['sub_questions']
        for s in sub_questions_data:
            s["variant_lesson"] = variant_lesson
            s["parent"] = question
        if sub_questions_data:
            sub_questions = sub_questions_serializer.create(sub_questions_data)
        # question_obj = Question.objects.filter(
        #     pk=question.id).prefetch_related(
        #     "sub_questions").first()
        return question


# --------------------------- views ------------------------------
class VariantView(generics.ListAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = VariantListSerializer
    queryset = Variant.objects.all()
    pagination_class = SimplePagination

    @swagger_auto_schema(tags=["super_admin"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


variant_list = VariantView.as_view()


class VariantLessonView(generics.ListAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = VariantLessonSerializer
    queryset = CourseTypeLesson.objects.all()

    @swagger_auto_schema(tags=["super_admin"])
    def get(self, request, *args, **kwargs):
        variant_id = self.kwargs['variant_id']
        data = super().get(request, *args, **kwargs).data
        for d in data:
            d['variant_id'] = variant_id
        return Response(data)


variant_lesson_view = VariantLessonView.as_view()


class CheckAddQuestion(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(tags=["super_admin"])
    def get(self, request, variant_id, lesson_id):
        add_question_status = True
        user = request.user
        # question = variant_lesson.questions.filter(parent__isnull=True)
        # question_count = question.count()
        # if variant_lesson.number_of_questions <= question_count:
        #     add_question_status = False
        # number = question_count + 1
        number = 0 + 1
        return Response({'status': add_question_status, 'number': number})


check_add_question_view = CheckAddQuestion.as_view()


class QuestionListView(generics.ListAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = QuestionAdminSerializer
    queryset = Question.objects.all()

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


class CommonQuestionListView(generics.ListAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListCommonQuestionSerializer
    queryset = CommonQuestion.objects.all().order_by('-id')

    @swagger_auto_schema(tags=["super_admin"])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


common_question_list_view = CommonQuestionListView.as_view()


class ImportQuestionsView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(tags=["super_admin"])
    def post(self, request, *args, **kwargs):
        variant_id = self.kwargs['variant_id']
        lesson_id = self.kwargs['lesson_id']
        variant = Variant.objects.get(pk=variant_id)
        with request.FILES['file'] as f:
            try:
                with transaction.atomic():
                    line = f.readline().decode().strip()
                    questions_texts = ""
                    count = 0
                    while True:
                        if not line.strip():
                            count += 1
                            question = create_question(
                                questions_texts=questions_texts,
                                variant_id=variant_id,
                                lesson_id=lesson_id,
                            )
                            if question is None:
                                return Response(
                                    {"detail": "Что то не так"},
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                            questions_texts = ""
                        elif line == 'end' or line == 'End':
                            pass
                            # if variant_lesson.variant.variant_type == VariantType.FULL:
                            #     # if count != variant_lesson.number_of_questions:
                            #     #     transaction.rollback()
                            #     break
                            # else:
                            #     break
                        else:
                            questions_texts += line.strip() + "new_line"
                        line = f.readline().decode().strip()
            except Exception as e:
                # if count != variant_lesson.number_of_questions:
                #     return Response(
                #         {"detail": "Неверное количество"},
                #         status=status.HTTP_400_BAD_REQUEST
                #     )
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response({"detail": "created"}, status=status.HTTP_201_CREATED)


import_question_view = ImportQuestionsView.as_view()


class AddQuestionView(generics.CreateAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = QuestionSerializer

    @swagger_auto_schema(tags=["super_admin"])
    def post(self, request, *args, **kwargs):
        answers = [ans for ans in self.request.data.get('answers') if
                   ans.get('answer')]
        request.data['answers'] = answers
        return self.create(request, *args, **kwargs)


add_question_view = AddQuestionView.as_view()
