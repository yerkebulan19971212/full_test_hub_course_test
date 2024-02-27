from rest_framework import serializers

from src.quizzes.serializers import AnswerSerializer
from src.quizzes.models import Question, CommonQuestion, StudentQuizz, \
    StudentQuizzFile, TestFullScore


class MyTestSerializer(serializers.ModelSerializer):
    quantity_question = serializers.IntegerField(default=120)
    name_kz = serializers.CharField(source='packet.name_kz', default="", read_only=True)
    name_ru = serializers.CharField(source='packet.name_ru', default="", read_only=True)
    name_en = serializers.CharField(source='packet.name_en', default="", read_only=True)

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
