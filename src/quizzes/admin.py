from django.contrib import admin
from .models import StudentQuizz

admin.site.register([
])


@admin.register(StudentQuizz)
class StudentQuizzAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'id', 'course_type', 'packet', 'status', 'lesson',
        'lesson_pair', 'quizz_type', 'language', 'quizz_start_time',
        'quizz_end_time', 'created',
        'modified')
    fields = (
        'user', 'id', 'course_type', 'packet', 'status', 'lesson',
        'lesson_pair', 'quizz_type', 'language', 'quizz_start_time',
        'quizz_end_time', 'created',
        'modified')
    readonly_fields = ('pk', 'created', 'modified')
    search_fields = (
        'user__email',
        'user__username',
        'user__phone',
    )
