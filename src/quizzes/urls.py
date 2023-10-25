from django.urls import include, path

from src.quizzes.api_views import (by_lesson_finish_view,
                                   by_lesson_pass_answer_view,
                                   by_lesson_quizz_lesson_view,
                                   by_lesson_quizz_question_view,
                                   by_lesson_quizz_view, finish_quiz_test,
                                   full_quizz_lesson_view,
                                   full_quizz_question_view, full_quizz_view,
                                   full_test_finish_view,
                                   get_flash_card_question,
                                   get_quiz_test_question_view, my_test_view,
                                   new_by_lesson_quizz_view,
                                   new_flash_card_view, new_full_test_view,
                                   new_quizz_test_view, pass_answer_view,
                                   pass_quizz_test_answer_view,
                                   quiz_test_check_answer_view,
                                   get_full_test_result_view,
                                   get_full_test_full_score_result_view,
                                   st_result_view)

full_test = [
    path('new/', new_full_test_view),
    path('<int:pk>/', full_quizz_view),
    path('lessons/<int:student_quizz>/', full_quizz_lesson_view),
    path('questions/', full_quizz_question_view),
    path('pass-answer/', pass_answer_view),
    path('finish/<int:student_quizz>/', full_test_finish_view),
    path('result/<int:pk>/', st_result_view),
    path('result-lesson/<int:pk>/', get_full_test_full_score_result_view),

    path('result-questions/', get_full_test_result_view),
]

by_lesson_quizz = [
    path('new/', new_by_lesson_quizz_view),
    path('<int:pk>/', by_lesson_quizz_view),
    path('lessons/<int:student_quizz>/', by_lesson_quizz_lesson_view),
    path('questions/', by_lesson_quizz_question_view),
    path('pass-answer/', by_lesson_pass_answer_view),
    path('finish/<int:student_quizz>/', by_lesson_finish_view),
]

flash_card = [
    path('new/', new_flash_card_view),
    path('questions/', get_flash_card_question),
]

quizz_test = [
    path('new/', new_quizz_test_view),
    path('question/<int:student_quizz>/', get_quiz_test_question_view),
    path('pass-answer/', pass_quizz_test_answer_view),
    path('check/<int:question_id>/', quiz_test_check_answer_view),
    path('finish/<int:student_quizz>/', finish_quiz_test),
]

api_v1_urlpatterns = [
    path('full-test/', include(full_test)),
    path('flash-card/', include(flash_card)),
    path('quizz-test/', include(quizz_test)),
    path('by-lesson/', include(by_lesson_quizz)),
    path('my-test-list/', my_test_view),

]

app_name = 'quizzes'
urlpatterns = [
    path('api/v1/', include(api_v1_urlpatterns)),
]
