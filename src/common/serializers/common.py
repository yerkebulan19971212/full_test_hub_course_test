import datetime

from rest_framework import serializers

from src.common import models
from src.common.models import BoughtPacket


class QuizzTypeSerializer(serializers.ModelSerializer):
    name_kz = serializers.CharField(source='quizz_type.name_kz')
    name_ru = serializers.CharField(source='quizz_type.name_ru')
    name_en = serializers.CharField(source='quizz_type.name_en')
    code = serializers.CharField(source='quizz_type.name_code')
    icon = serializers.ImageField(source='quizz_type.icon')
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
            'code',
        )


class PacketSerializer(serializers.ModelSerializer):
    remainder = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = models.Packet
        fields = (
            'id',
            'days',
            'price',
            'packet_type',
            'quantity',
            'remainder',
            'status'
        )

    def get_remainder(self, obj):
        user = self.context['request'].user
        print(obj.id)
        packet = BoughtPacket.objects.filter(
            user=user,
            packet_id=obj.id,
            status=True
        )
        if packet:
            return packet.first().remainder
        return 0

    def get_status(self, obj):
        user = self.context['request'].user
        packet = BoughtPacket.objects.filter(
            user=user,
            packet_id=obj.id,
            status=True
        )
        if packet:
            return True
        return False


class BuyPacketSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BoughtPacket
        fields = (
            'packet',
        )

    def create(self, validated_data):
        packet = validated_data['packet']
        validated_data[
            'end_time'] = datetime.datetime.now() + datetime.timedelta(
            days=packet.days)
        validated_data['price'] = packet.price
        validated_data['remainder'] = packet.quantity
        return super().create(validated_data)
