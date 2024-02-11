from django.urls import include, path

from src.quizzes.api_views import (by_lesson_finish_view,
                                   by_lesson_pass_answer_view,
                                   by_lesson_quizz_lesson_view,
                                   by_lesson_quizz_question_view,
                                   by_lesson_quizz_view,
                                   result_rating,
                                   by_lesson_result_task_progress_view,
                                   by_lesson_result_view, finish_quiz_test,
                                   full_quizz_lesson_view,
                                   full_quizz_question_view, full_quizz_view,
                                   full_test_finish_view,
                                   get_by_lesson_full_score_result_view,
                                   get_by_lesson_result_question,
                                   get_files_view, get_flash_card_question,
                                   get_full_test_full_score_result_view,
                                   get_quiz_test_question_view,
                                   get_result_question, my_test_view,
                                   new_by_lesson_quizz_view,
                                   new_flash_card_view, new_full_test_view,
                                   new_quizz_test_view, pass_answer_view,
                                   pass_quizz_test_answer_view,
                                   result_quiz_test_view,
                                   finish_flash_card_view,
                                   get_quiz_test_question_by_id_view,
                                   quiz_test_check_answer_view, st_result_view,
                                   pass_flash_card_question,
                                   result_flash_card_question,
                                   repeat_flash_card_view)

full_test = [
    path('new/', new_full_test_view),
    path('<int:pk>/', full_quizz_view),
    path('lessons/<int:student_quizz>/', full_quizz_lesson_view),
    path('questions/', full_quizz_question_view),
    path('pass-answer/', pass_answer_view),
    path('finish/<int:student_quizz>/', full_test_finish_view),
    path('result/<int:pk>/', st_result_view),
    path('result-lesson/<int:pk>/', get_full_test_full_score_result_view),
    path('result-questions/<int:pk>/<int:student_quizz_id>/',
         get_result_question),
]

by_lesson_quizz = [
    path('new/', new_by_lesson_quizz_view),
    path('<int:pk>/', by_lesson_quizz_view),
    path('lessons/<int:student_quizz>/', by_lesson_quizz_lesson_view),
    path('questions/', by_lesson_quizz_question_view),
    path('pass-answer/', by_lesson_pass_answer_view),
    path('finish/<int:student_quizz>/', by_lesson_finish_view),
    path('result/<int:pk>/', by_lesson_result_view),
    path('result-lesson/<int:pk>/', get_by_lesson_full_score_result_view),
    path('task-progress/<int:pk>/', by_lesson_result_task_progress_view),
    path('result-questions/<int:pk>/<int:student_quizz_id>/',
         get_by_lesson_result_question),
]

flash_card = [
    path('new/', new_flash_card_view),
    path('questions/', get_flash_card_question),
    path('pass-question/', pass_flash_card_question),
    path('result/<int:student_quizz>/', result_flash_card_question),
    path('finish/<int:student_quizz>/', finish_flash_card_view),
    path('repeat/<int:student_quizz>', repeat_flash_card_view),
]

quizz_test = [
    path('new/', new_quizz_test_view),
    path('question/<int:student_quizz>/', get_quiz_test_question_view),
    path('question/<int:student_quizz>/<int:question_id>/',
         get_quiz_test_question_by_id_view),
    path('pass-answer/', pass_quizz_test_answer_view),
    path('check/<int:question_id>/', quiz_test_check_answer_view),
    path('finish/<int:student_quizz>/', finish_quiz_test),
    path('result/<int:student_quizz>/', result_quiz_test_view),
]

api_v1_urlpatterns = [
    path('full-test/', include(full_test)),
    path('flash-card/', include(flash_card)),
    path('quizz-test/', include(quizz_test)),
    path('by-lesson/', include(by_lesson_quizz)),
    path('my-test-list/', my_test_view),
    path('get-files/', get_files_view),
    path('result-rating/', result_rating),
]

app_name = 'quizzes'
urlpatterns = [
    path('api/v1/', include(api_v1_urlpatterns)),
]
