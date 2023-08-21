from django.urls import path, include
from src.quizzes.api_views import (new_flash_card_view, new_quizz_test_view,
                                   get_flash_card_question,
                                   get_quiz_test_question_view,
                                   pass_quizz_test_answer_view,
                                   quiz_test_check_answer_view,
                                   finish_quiz_test, new_full_test_view,
                                   full_quizz_view)


full_test = [
    path('new/', new_full_test_view),
    path('<int:pk>/', full_quizz_view),
    # path('questions/', get_flash_card_question),
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

]

app_name = 'quizzes'
urlpatterns = [
    path('api/v1/', include(api_v1_urlpatterns)),
]
