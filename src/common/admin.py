from django.contrib import admin

from .models import (Lesson, LessonPair, QuizzType, CourseTypeQuizz, Packet)

admin.site.register([
    LessonPair,
    QuizzType,
    CourseTypeQuizz,
    Packet
])
# Register your models here.
