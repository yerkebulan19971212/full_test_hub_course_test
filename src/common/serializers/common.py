import datetime

from django.utils import timezone
from rest_framework import serializers

from src.common import models
from src.common.abstract_serializer import NameSerializer
from src.common.constant import PromoCodeType
from src.common.exception import PromoCodeNotExistsError, PassedTestError, \
    PromoCodeUsedError
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
            'uuid',
            'name_code',
            'name_kz',
            'name_ru',
            'name_en',
            'days',
            'img',
            'price',
            'second_price',
            'packet_type',
            'quantity',
            'remainder',
            'status'
        )

    def get_remainder(self, obj):
        user = self.context['request'].user
        now = timezone.now()
        packet = BoughtPacket.objects.filter(
            user=user,
            packet_id=obj.id,
            status=True,
            start_time__lte=now,
            end_time__gte=now
        )
        if packet:
            return obj.quantity - packet.first().remainder
        return 0

    def get_status(self, obj):
        user = self.context['request'].user
        now = timezone.now()
        packet = BoughtPacket.objects.filter(
            user=user,
            packet_id=obj.id,
            status=True,
            start_time__lte=now,
            end_time__gte=now,
        )
        if packet:
            return True
        return False


class PacketTestSerializer(NameSerializer):
    class Meta:
        model = models.PacketTestType
        fields = [
            'name'
        ]


class PacketDetailSerializer(NameSerializer):
    packet_test_type = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = models.Packet
        fields = (
            'uuid',
            'name_code',
            'name',
            'name_kz',
            'name_ru',
            'name_en',
            'days',
            'img',
            'price',
            'packet_type',
            'packet_test_type',
            'quantity',
            'question_quantity',
            'duration',
            'subject_quantity',
            'description',
        )

    def get_packet_test_type(self, obj):
        if obj.packet_test_type:
            return PacketTestSerializer(obj.packet_test_type, context=self.context).data
        return None

    def get_price(self, obj):
        if obj.second_price > 0:
            return obj.second_price
        return obj.price


class BuyPacketSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BoughtPacket
        fields = (
            'packet',
        )

    def create(self, validated_data):
        packet = validated_data['packet']
        price = packet.second_price if packet.second_price else packet.price
        user = self.context['request'].user
        validated_data['user'] = user
        end_time = datetime.datetime.now() + datetime.timedelta(
            days=packet.days)
        validated_data['end_time'] = end_time
        validated_data['price'] = price
        validated_data['remainder'] = packet.quantity
        user.balance -= price
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
            end_date__gte=now.date(),
            is_active=True,
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


class SupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Support
        fields = (
            'question',
            'comment'
        )

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class TelegramPromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = (
            'name_code',
        )
