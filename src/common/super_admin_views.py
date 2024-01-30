from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, serializers, permissions
from rest_framework.response import Response

from src.common.models import CourseTypeLesson, Lesson
from src.common.paginations import SimplePagination
from src.quizzes.models import Variant, Question


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


class QuestionListSerializer(serializers.ModelSerializer):
    number = serializers.IntegerField(source='order')
    sum_of_question = serializers.IntegerField(default=40)
    number_of_questions = serializers.IntegerField(default=0)
    lesson = LessonSerializer()

    class Meta:
        model = Question
        fields = [
            'id',
            'number',
            'common_question',
            'question',
            'sub_questions',
            'answers',
        ]


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


class QuestionListView(generics.ListAPIView):
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


question_list_view = QuestionListView.as_view()
