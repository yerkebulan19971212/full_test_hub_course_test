import datetime

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from src.common import abstract_serializer
from src.common.models import CourseType, Lesson, QuizzType, LessonPair, \
    CourseTypeQuizz
from src.common.utils import get_multi_score
from src.quizzes.models import StudentQuizz, Question, Answer, StudentAnswer, \
    StudentScore
from src.quizzes.models.student_quizz import StudentQuizzQuestion


class FullQuizzSerializer(serializers.ModelSerializer):
    lessons = serializers.ListSerializer(
        child=serializers.IntegerField(required=True),
        required=True, write_only=True
    )
    quizz_type = serializers.CharField(default='full_test', write_only=True)

    class Meta:
        model = StudentQuizz
        fields = (
            'id',
            'language',
            'lessons',
            'packet'
        )

    def create(self, validated_data):
        lessons = validated_data.pop("lessons")
        quizz_type = validated_data.pop("quizz_type")

        lesson_pair = LessonPair.objects.filter(
            Q(lesson_1=lessons[0], lesson_2=lessons[1]) |
            Q(lesson_1=lessons[1], lesson_2=lessons[0])
        ).first()
        c = CourseTypeQuizz.objects.filter(
            quizz_type__name_code=quizz_type).first()
        language = validated_data.get("language")
        validated_data["quizz_start_time"] = datetime.datetime.now()
        validated_data["quizz_type"] = c
        validated_data["course_type"] = CourseType.objects.get_ent()
        validated_data["lesson_pair"] = lesson_pair
        validated_data["quizz_duration"] = c.course_type.quizz_duration
        student_quizz = super().create(validated_data)
        questions = []
        questions += Question.objects.get_history_full_test(language)
        questions += Question.objects.get_reading_literacy_full_test(language)
        questions += Question.objects.get_mat_full_test(language)
        questions += Question.objects.get_full_test(language,
                                                    lesson_pair.lesson_1)
        questions += Question.objects.get_full_test(language,
                                                    lesson_pair.lesson_2)
        StudentQuizzQuestion.objects.bulk_create([StudentQuizzQuestion(
            order=i,
            question=q,
            lesson_id=q.lesson_question_level.test_type_lesson.lesson_id,
            student_quizz=student_quizz
        ) for i,q in enumerate(questions)])

        return student_quizz


class StudentQuizzInformationSerializer(serializers.ModelSerializer):
    # number_of_attempts = serializers.IntegerField(default=1)
    # duration = serializers.SerializerMethodField()
    # permission_to_pass = serializers.SerializerMethodField()
    # result = serializers.SerializerMethodField()

    class Meta:
        model = StudentQuizz
        fields = (
            'id',
            'status',
            # 'result',
            # 'duration',
            # 'permission_to_pass',
        )

    def get_permission_to_pass(self, obj):
        now = timezone.now()
        if obj.end_time < now:
            return False
        return True

    def get_duration(self, obj):
        seconds = obj.variant.duration.total_seconds()
        return seconds // 60

    # def get_result(self, obj):
    #     if obj.status == "NOT_PASSED":
    #         return {}
    #     user = obj.user
    #     variant = obj.variant
    #     student_ent_result = StudentEntResult.objects.filter(
    #         student=user, variant=variant).first()
    #     context = self.context
    #     return StudentEntResultSerializer(
    #         student_ent_result, context=context).data


class FullQuizLessonListSerializer(abstract_serializer.NameSerializer):
    correct = serializers.IntegerField(default=0)
    sum_of_questions = serializers.IntegerField(default=0)
    sum_of_point = serializers.IntegerField(default=120)
    number = serializers.IntegerField(default=1)
    score = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            'id',
            'name',
            'number',
            'correct',
            'score',
            'sum_of_point',
            'sum_of_questions'
        )

    # def get_name(self, obj):
    #     test_id = self.context['view'].kwargs.get('test_id')
    #     student_test = StudentQuizz.objects.select_related(
    #             'variant'
    #         ).get(pk=test_id)
    #     variant = student_test.variant
    #     if variant.test_lang == 1:
    #         return obj.name_ru
    #     return obj.name_kz

    def get_score(self, obj):
        return 0


class StudentAnswersSerializer(serializers.Serializer):
    question = serializers.IntegerField(required=True, write_only=True)
    student_quizz = serializers.IntegerField(required=True, write_only=True)
    answers = serializers.ListSerializer(
        child=serializers.IntegerField(required=True),
        required=True, write_only=True
    )
