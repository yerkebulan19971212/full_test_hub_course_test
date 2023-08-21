import datetime

from django.utils import timezone
from rest_framework import serializers

from src.common.constant import QuizzType, ChoiceType
from src.common.models import CourseType
from src.quizzes.models import StudentQuizz, Question, Answer
from src.quizzes.models.student_quizz import StudentQuizzQuestion


class FullQuizzSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentQuizz
        fields = (
            'id',
            'language',
            'lesson_pair',
        )

    def create(self, validated_data):
        lesson_pair = validated_data.get("lesson_pair")
        language = validated_data.get("language")
        validated_data["quizz_start_time"] = datetime.datetime.now()
        validated_data["quizz_type"] = QuizzType.FULL_TEST_ENT
        validated_data["course_type"] = CourseType.objects.get_ent()
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
            question=q,
            student_quizz=student_quizz
        ) for q in questions])

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
