from django.contrib import admin

from .models import (BoughtPacket, City, Country, CourseType, CourseTypeLesson,
                     CourseTypeQuizz, KaspiPay, Lesson, LessonPair, Packet,
                     QuizzType, School, PromoCode, Support, UserPromoCode)
from src.quizzes.admin import VariantPacketInline

admin.site.register([
    BoughtPacket,
    City,
    Country,
    CourseType,
    CourseTypeLesson,
    CourseTypeQuizz,
    KaspiPay,
    Lesson,
    LessonPair,
    QuizzType,
    School,
    PromoCode,
    UserPromoCode
])


@admin.register(Support)
class SupportAdmin(admin.ModelAdmin):
    list_display = [
        'question',
        'created',
        'comment'
    ]


@admin.register(Packet)
class PacketAdmin(admin.ModelAdmin):
    inlines = [VariantPacketInline]

    list_display = (
        'name_code',
        'pk',
        'order',
        'is_active',
        'name_kz',
        'name_ru',
        'name_en',
        'quizz_type',
        'days',
        'price',
        'packet_type',
        'quantity',
        'uuid',
        'created',
        'modified'
    )
    fields = (
        'name_code',
        'name_kz',
        'order',
        'pk',
        'name_ru',
        'name_en',
        'quizz_type',
        'days',
        'price',
        'packet_type',
        'quantity',
        'created',
        'modified'
    )
    readonly_fields = ('pk', 'uuid', 'created', 'modified')
    search_fields = (
        'pk',
        'uuid',
        'name_kz',
        'name_ru',
        'name_en'
    )
