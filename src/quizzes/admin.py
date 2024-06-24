from django.contrib import admin
from .models import StudentQuizz, StudentQuizzFile, Question, QuestionLevel, \
    Variant, LessonQuestionLevel, CommonQuestion
from .models.variant import VariantPacket

admin.site.register([
    QuestionLevel,
    StudentQuizzFile,
    LessonQuestionLevel,
    CommonQuestion
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
        'level_name',
        # 'lesson_question_level__question_level__name_code',
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
        'lesson_question_level__test_type_lesson__lesson',
        'question_type',
    ]
    readonly_fields = ('pk', 'created', 'modified')
    search_fields = (
        'question',
        'common_question__text',
        'common_question__name_code',
    )


class VariantPacketInline(admin.TabularInline):
    model = VariantPacket
    extra = 1


@admin.register(Variant)
class QuestionQuizzAdmin(admin.ModelAdmin):
    inlines = [VariantPacketInline]
    list_display = (
        'name_code', 'id', 'is_active', 'created',
    )
    list_filter = []
    readonly_fields = ('pk', 'created', 'modified')
    search_fields = (
        'name_kz',
        'name_ru',
        'name_en',
        'name_code',
    )
