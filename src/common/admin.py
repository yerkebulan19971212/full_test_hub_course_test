from django.contrib import admin

from .models import (BoughtPacket, City, Country, CourseType, CourseTypeLesson,
                     CourseTypeQuizz, KaspiPay, Lesson, LessonPair, Packet,
                     QuizzType)

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
    QuizzType
])


@admin.register(Packet)
class PacketAdmin(admin.ModelAdmin):
    list_display = (
        'name_kz',
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
    fields = (
        'name_kz',
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
    readonly_fields = ('pk', 'created', 'modified')
    search_fields = ('name_kz', 'name_ru', 'name_en')
