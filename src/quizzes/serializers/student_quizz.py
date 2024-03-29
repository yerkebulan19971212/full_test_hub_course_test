import datetime

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from config.celery import student_user_question_count
from src.common import abstract_serializer
from src.common.models import CourseType, Lesson, QuizzType, LessonPair, \
    CourseTypeQuizz, BoughtPacket, Packet
from src.common.utils import get_multi_score
from src.quizzes.models import StudentQuizz, Question, Answer, StudentAnswer, \
    StudentScore
from src.quizzes.models.student_quizz import StudentQuizzQuestion


class ByLessonQuizzSerializer(serializers.ModelSerializer):
    quiz_type = serializers.CharField(write_only=True)

    class Meta:
        model = StudentQuizz
        fields = (
            'id',
            'language',
            'lesson',
            'quiz_type'
        )

    def create(self, validated_data):
        language = validated_data.get("language")
        lesson = validated_data.get("lesson")
        packet_id = validated_data.pop("quiz_type", None)
        quizz_type = CourseTypeQuizz.objects.filter(
            quizz_type__name_code='by_lesson').first()
        packet = Packet.objects.filter(id=int(packet_id)).first()
        validated_data[
            "quizz_duration"] = packet.quizz_type.quizz_type.quizz_duration
        user = self.context["request"].user
        validated_data['user'] = user
        validated_data["quizz_start_time"] = datetime.datetime.now()
        validated_data["quizz_type"] = quizz_type
        course_type = CourseType.objects.get_ent()
        validated_data["course_type"] = course_type
        student_quizz = super().create(validated_data)
        questions = Question.objects.get_questions_by_lesson(
            lang=language,
            lesson=lesson,
            user=self.context["request"].user,
            packet=packet, quizz_type=quizz_type
        )
        StudentQuizzQuestion.objects.bulk_create([StudentQuizzQuestion(
            question=q,
            lesson=lesson,
            student_quizz=student_quizz
        ) for q in questions])
        question_ids = [q.id for q in questions]
        student_user_question_count.delay(user.id, question_ids, quizz_type.id)
        if packet is not None:
            bought_packet = BoughtPacket.objects.filter(
                user=user,
                packet=packet,
                status=True
            ).first()
            if bought_packet.remainder == 1:
                bought_packet.status = False
            bought_packet.remainder -= 1
            bought_packet.save()
            student_quizz.bought_packet = bought_packet
            student_quizz.packet = packet
            student_quizz.save()

        return student_quizz
