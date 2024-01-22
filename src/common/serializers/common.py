import datetime

from django.utils import timezone
from rest_framework import serializers

from src.common import models
from src.common.exception import PromoCodeNotExistsError, PassedTestError, PromoCodeUsedError
from src.common.models import BoughtPacket, PromoCode, UserPromoCode


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
            'name_code',
            'name_kz',
            'name_ru',
            'name_en',
            'days',
            'price',
            'packet_type',
            'quantity',
            'remainder',
            'status'
        )

    def get_remainder(self, obj):
        user = self.context['request'].user
        packet = BoughtPacket.objects.filter(
            user=user,
            packet_id=obj.id,
            status=True
        )
        if packet:
            return obj.quantity - packet.first().remainder
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
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data[
            'end_time'] = datetime.datetime.now() + datetime.timedelta(
            days=packet.days)
        validated_data['price'] = packet.price
        validated_data['remainder'] = packet.quantity
        user.balance -= packet.price
        user.save()
        return super().create(validated_data)


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.City
        fields = (
            'id',
            'name_kz',
            'name_ru',
            'name_en',
        )


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.School
        fields = (
            'id',
            'name_kz',
            'name_ru',
            'name_en',
        )


class RatingTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RatingTest
        fields = (
            'id',
            'start_time',
            'end_time',
        )


class PromoCodeSerializer(serializers.ModelSerializer):
    promo_code = serializers.CharField(required=True)

    class Meta:
        model = models.UserPromoCode
        fields = (
            'promo_code',
        )

    def create(self, validated_data):
        promo_code = validated_data['promo_code']
        user = self.context['request'].user
        now = datetime.datetime.now()
        promo_code_obj = PromoCode.objects.filter(
            name_code=promo_code,
            start_date__lte=now.date(),
            end_date__gte=now.date()
        )
        if not promo_code_obj.exists():
            raise PromoCodeNotExistsError()

        user_promo_code = models.UserPromoCode.objects.filter(
            promo_code__name_code=promo_code,
            user=user
        )
        if user_promo_code.exists():
            raise PromoCodeUsedError()
        user.balance += promo_code_obj.first().bonus
        user.save()
        instance = UserPromoCode.objects.create(
            user=user,
            promo_code=promo_code_obj.first(),
            balance=promo_code_obj.first().bonus
        )
        return instance
