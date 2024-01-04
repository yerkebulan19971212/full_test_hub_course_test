from django.contrib import admin
from .models import StudentQuizz, StudentQuizzFile, Question, QuestionLevel, \
    Variant

admin.site.register([
    QuestionLevel,
    StudentQuizzFile,
    Variant
])


@admin.register(StudentQuizz)
class StudentQuizzAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'id', 'course_type', 'packet', 'status', 'lesson',
        'lesson_pair', 'quizz_type', 'language', 'quizz_start_time',
        'quizz_end_time', 'created',
        'modified'
    )
    fields = (
        'user', 'id', 'course_type', 'packet', 'status', 'lesson',
        'lesson_pair', 'quizz_type', 'language', 'quizz_start_time',
        'quizz_end_time', 'created',
        'modified'
    )
    readonly_fields = ('pk', 'created', 'modified')
    search_fields = (
        'user__email',
        'user__username',
        'user__phone',
    )


@admin.register(Question)
class QuestionQuizzAdmin(admin.ModelAdmin):
    list_display = (
        'short_question', 'question_type', 'id',
    )
    # fields = (
    #     'user', 'id', 'course_type', 'packet', 'status', 'lesson',
    #     'lesson_pair', 'quizz_type', 'language', 'quizz_start_time',
    #     'quizz_end_time', 'created',
    #     'modified'
    # )
    list_filter = [
        'variant',
        'lesson_question_level__question_level',
        'question_type',
    ]
    readonly_fields = ('pk', 'created', 'modified')
    search_fields = (
        'question',
        'common_question__text',
        'common_question__name_code',
    )
