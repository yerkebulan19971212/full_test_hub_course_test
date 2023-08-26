from django.contrib import admin

from .models import (Lesson, LessonPair, QuizzType, CourseTypeQuizz)

admin.site.register([
    LessonPair,
    QuizzType,
    CourseTypeQuizz
])
# Register your models here.
