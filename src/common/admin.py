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
    Packet,
    QuizzType
])
