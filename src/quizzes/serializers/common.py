import datetime

from django.conf import settings
from django.db.models import Q
from rest_framework import serializers

from config.celery import student_user_question_count
from src.common.exception import DoesNotHaveTest
from src.common import exception
from src.common.models import BoughtPacket, LessonPair, CourseType, Lesson
from src.quizzes.serializers import AnswerSerializer
from src.quizzes.models import Question, CommonQuestion, StudentQuizz, \
    StudentQuizzFile, TestFullScore, StudentQuizzQuestion


class MyTestSerializer(serializers.ModelSerializer):
    quantity_question = serializers.IntegerField(default=120)
    name_kz = serializers.CharField(source='packet.name_kz', default="",
                                    read_only=True)
    name_ru = serializers.CharField(source='packet.name_ru', default="",
                                    read_only=True)
    name_en = serializers.CharField(source='packet.name_en', default="",
                                    read_only=True)

    class Meta:
        model = StudentQuizz
        fields = (
            'id',
            'name_kz',
            'name_ru',
            'name_en',
            'quizz_start_time',
            'quizz_end_time',
            'status',
            'quizz_duration',
            'quantity_question'
        )


class StudentQuizzFileSerializer(serializers.ModelSerializer):
    size = serializers.SerializerMethodField()

    class Meta:
        model = StudentQuizzFile
        fields = (
            'id',
            'icon',
            'file',
            'file_name',
            'size',
        )

    def get_size(self, obj):
        return obj.file.size / 1024 / 1024


class MyProgressSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(source='student_quizz__created')
    score_sum = serializers.IntegerField()

    class Meta:
        model = TestFullScore
        fields = (
            'date',
            'score_sum',
        )


class MyLessonProgressSerializer(serializers.ModelSerializer):
    name_kz = serializers.CharField(source='lesson__name_kz')
    name_ru = serializers.CharField(source='lesson__name_ru')
    name_en = serializers.CharField(source='lesson__name_en')
    icon = serializers.SerializerMethodField()
    main = serializers.BooleanField(source='lesson__course_type_lessons__main')
    score_sum = serializers.IntegerField()

    class Meta:
        model = TestFullScore
        fields = (
            'main',
            'name_kz',
            'name_ru',
            'name_en',
            'icon',
            'score_sum',
        )

    def get_icon(self, obj):
        if obj.get('lesson__icon'):  # Check if icon exists
            return "/".join(
                [settings.MEDIA_ROOT, 'media', obj.get('lesson__icon')])
        return None


class NewTestSerializer(serializers.ModelSerializer):
    lessons = serializers.ListSerializer(
        child=serializers.IntegerField(required=True),
        required=True, write_only=True
    )
    question_number = serializers.IntegerField(default=10, write_only=True)

    class Meta:
        model = StudentQuizz
        fields = (
            'id',
            'language',
            'lessons',
            'packet',
            'question_number'
        )

    def create(self, validated_data):
        user = self.context["request"].user
        lessons = validated_data.pop("lessons")
        packet = validated_data.get("packet")
        question_number = validated_data.pop("question_number")
        language = validated_data.get("language")
        bought_packet = BoughtPacket.objects.filter(
            user=user,
            packet=packet,
            status=True
        ).first()
        if not bought_packet or bought_packet.remainder < 1:
            raise exception.DoesNotHaveTest()
        if bought_packet.remainder == 1:
            bought_packet.status = False
        bought_packet.remainder -= 1
        bought_packet.save()
        lesson_pair = None
        lesson = None
        if len(lessons) > 1:
            lesson_pair = LessonPair.objects.filter(
                Q(lesson_1=lessons[0], lesson_2=lessons[-1]) |
                Q(lesson_1=lessons[-1], lesson_2=lessons[0])
            ).first()
            validated_data["lesson_pair"] = lesson_pair
        else:
            lesson = Lesson.objects.get(pk=lessons[0])
            validated_data["lesson"] = lesson

        validated_data["quizz_start_time"] = datetime.datetime.now()
        validated_data[
            "quizz_duration"] = packet.quizz_type.quizz_type.quizz_duration
        validated_data["course_type"] = CourseType.objects.get_ent()
        validated_data["user"] = user
        validated_data["quizz_type"] = packet.quizz_type
        student_quizz = super().create(validated_data)
        student_quizz.bought_packet = bought_packet
        student_quizz.save()

        questions = []
        quizz_type = packet.quizz_type
        quizz_type_name = quizz_type.quizz_type.name_code
        if quizz_type_name in ['full_test', 'rating']:
            questions += Question.objects.get_history_full_test_v2(
                language, packet, user, quizz_type
            )
            questions += Question.objects.get_reading_literacy_full_test_v2(
                language, packet, user, quizz_type)
            if lesson_pair:
                if lesson_pair.lesson_1.name_code != 'creative_exam':
                    questions += Question.objects.get_mat_full_test_v2(
                        language, packet, user, quizz_type)
                    questions += Question.objects.get_full_test_v2(
                        language, lesson_pair.lesson_1, packet, user,
                        quizz_type)
                    questions += Question.objects.get_full_test_v2(
                        language, lesson_pair.lesson_2, packet, user,
                        quizz_type)
        elif quizz_type_name == 'by_lesson':
            questions += Question.objects.get_questions_by_lesson(
                lang=language,
                lesson=lesson,
                user=user,
                packet=packet,
                quizz_type=quizz_type
            )
        elif quizz_type_name == 'flash_card':
            questions = list(Question.objects.get_questions_for_flash_card(
                language,
                lesson,
                question_number,
                packet
            ))
        StudentQuizzQuestion.objects.bulk_create([StudentQuizzQuestion(
            order=i,
            question=q,
            lesson_id=q.lesson_question_level.test_type_lesson.lesson_id,
            student_quizz=student_quizz
        ) for i, q in enumerate(questions)])
        question_ids = [q.id for q in questions]
        student_user_question_count.delay(user.id, question_ids, quizz_type.id)
        return student_quizz
