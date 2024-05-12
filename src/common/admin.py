from django.contrib import admin

from .models import (BoughtPacket, City, Country, CourseType, CourseTypeLesson,
                     CourseTypeQuizz, KaspiPay, Lesson, LessonPair, Packet,
                     QuizzType, School, PromoCode, Support, UserPromoCode, Blog, BlogCategory, PacketTestType)
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
    UserPromoCode,
    Blog,
    BlogCategory,
PacketTestType
])


@admin.register(Support)
class SupportAdmin(admin.ModelAdmin):
    list_display = [
        'question_id',
        'created',
        'comment'
    ]
    fields = [
        'pk',
        'question',
        'user',
        'comment',
        'created',
        'modified'
    ]
    raw_id_fields = ('user', 'question')
    readonly_fields = (
        'pk', 'uuid', 'created', 'modified'
    )
    list_select_related = ('user', 'question')
    search_fields = (
        'pk',
        'uuid',
        'question__question'
    )


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
        'second_price',
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
        'second_price',
        'img',
        'packet_type',
        'packet_test_type',
        'quantity',
        'question_quantity',
        'duration',
        'subject_quantity',
        'is_active',
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
