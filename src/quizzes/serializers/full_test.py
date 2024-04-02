import datetime

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from config.celery import student_user_question_count
from src.accounts.api_views.serializers import UserBaseSerializer
from src.common import abstract_serializer
from src.common.exception import UnexpectedError, DoesNotHaveTest
from src.common.models import CourseType, Lesson, QuizzType, LessonPair, \
    CourseTypeQuizz, BoughtPacket, Packet
from src.common.utils import get_multi_score
from src.quizzes.models import StudentQuizz, Question, Answer, StudentAnswer, \
    StudentScore, TestFullScore
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
            'packet',
            'quizz_type'
        )

    def create(self, validated_data):

        lessons = validated_data.pop("lessons")
        quizz_type = validated_data.pop("quizz_type")
        packet = validated_data.get("packet")
        user = self.context["request"].user
        validated_data['user'] = user

        if quizz_type == 'rating':
            packet = Packet.objects.filter(name_code='quizz_type').first()
            quizz_type = 1
        bought_packet = BoughtPacket.objects.filter(
            user=user,
            packet=packet,
            status=True
        ).first()
        if not bought_packet:
            raise UnexpectedError()
        if bought_packet.remainder < 1:
            raise DoesNotHaveTest()
        lesson_pair = LessonPair.objects.filter(
            Q(lesson_1=lessons[0], lesson_2=lessons[-1]) |
            Q(lesson_1=lessons[-1], lesson_2=lessons[0])
        ).first()
        quizz_type = CourseTypeQuizz.objects.get(
            quizz_type__name_code=quizz_type)
        language = validated_data.get("language")
        validated_data["quizz_start_time"] = datetime.datetime.now()
        validated_data["quizz_type"] = quizz_type
        validated_data["course_type"] = CourseType.objects.get_ent()
        validated_data["lesson_pair"] = lesson_pair
        validated_data[
            "quizz_duration"] = packet.quizz_type.quizz_type.quizz_duration
        student_quizz = super().create(validated_data)
        questions = []
        questions += Question.objects.get_history_full_test_v2(language,
                                                               packet, user,
                                                               quizz_type)
        questions += Question.objects.get_reading_literacy_full_test_v2(
            language, packet, user, quizz_type)
        if lesson_pair.lesson_1.name_code != 'creative_exam':
            questions += Question.objects.get_mat_full_test_v2(language,
                                                               packet, user,
                                                               quizz_type)
            questions += Question.objects.get_full_test_v2(language,
                                                           lesson_pair.lesson_1,
                                                           packet, user,
                                                           quizz_type)
            questions += Question.objects.get_full_test_v2(language,
                                                           lesson_pair.lesson_2,
                                                           packet, user,
                                                           quizz_type)
        StudentQuizzQuestion.objects.bulk_create([StudentQuizzQuestion(
            order=i,
            question=q,
            lesson_id=q.lesson_question_level.test_type_lesson.lesson_id,
            student_quizz=student_quizz
        ) for i, q in enumerate(questions)])
        question_ids = [q.id for q in questions]
        student_user_question_count.delay(user.id, question_ids, quizz_type.id)
        if bought_packet.remainder == 1:
            bought_packet.status = False
        bought_packet.remainder -= 1
        bought_packet.save()
        student_quizz.bought_packet = bought_packet
        student_quizz.save()

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
    sum_of_questions = serializers.SerializerMethodField()
    # sum_of_point = serializers.IntegerField(default=120)
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
            # 'sum_of_point',
            'sum_of_questions'
        )

    def get_sum_of_questions(self, obj):
        student_id = self.context["view"].kwargs.get('student_quizz')
        return StudentQuizzQuestion.objects.filter(student_quizz_id=student_id,
                                                   lesson=obj).count()

    def get_score(self, obj):
        return 0


class StudentAnswersSerializer(serializers.Serializer):
    question = serializers.IntegerField(required=True, write_only=True)
    student_quizz = serializers.IntegerField(required=True, write_only=True)
    answers = serializers.ListSerializer(
        child=serializers.IntegerField(required=True),
        required=True, write_only=True
    )


class TestFullScoreRatingSerializer(serializers.ModelSerializer):
    name_kz = serializers.CharField(source='lesson.name_kz')
    name_ru = serializers.CharField(source='lesson.name_ru')
    name_en = serializers.CharField(source='lesson.name_en')

    class Meta:
        model = TestFullScore
        fields = (
            'id',
            'lesson_id',
            'score',
            'name_kz',
            'name_ru',
            'name_en',
        )


class StudentQuizzRatingSerializer(serializers.ModelSerializer):
    is_current = serializers.BooleanField(default=False)
    max_score = serializers.IntegerField(default=140)
    total = serializers.IntegerField(source='total_count', default=0)
    math = serializers.IntegerField(default=0)
    literacy = serializers.IntegerField(default=0)
    history = serializers.IntegerField(default=0)
    city = serializers.CharField(source="student_quizz__user__city__name_ru",
                                 default="")
    lesson_1_ru = serializers.CharField(default="0")
    lesson_1_kz = serializers.CharField(default="0")
    lesson_1_en = serializers.CharField(default="0")
    lesson_2_ru = serializers.CharField(default="0")
    lesson_2_kz = serializers.CharField(default="0")
    lesson_2_en = serializers.CharField(default="0")
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = TestFullScore
        fields = (
            # 'student_quizz',
            'is_current',
            'full_name',
            'city',
            'max_score',
            'total',
            'math',
            'literacy',
            'history',
            'lesson_1_ru',
            'lesson_1_kz',
            'lesson_1_en',
            'lesson_2_ru',
            'lesson_2_kz',
            'lesson_2_en',
        )

    @staticmethod
    def get_full_name(obj):
        return f"{obj.get('student_quizz__user__first_name', '')} {obj.get('student_quizz__user__last_name', '')}"
