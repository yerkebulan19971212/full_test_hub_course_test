from rest_framework import serializers

from src.common import models


class QuizzTypeSerializer(serializers.ModelSerializer):
    name_kz = serializers.CharField(source='quizz_type.name_kz')
    name_ru = serializers.CharField(source='quizz_type.name_ru')
    name_en = serializers.CharField(source='quizz_type.name_en')
    icon = serializers.CharField(source='quizz_type.icon')
    color = serializers.CharField(source='quizz_type.color')

    class Meta:
        model = models.CourseTypeQuizz
        fields = (
            'id',
            'name_kz',
            'name_ru',
            'name_en',
            'icon',
            'color',
        )


class PacketSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Packet
        fields = (
            'id',
            'days',
            'price',
            'packet_type',
            'quantity',
        )
