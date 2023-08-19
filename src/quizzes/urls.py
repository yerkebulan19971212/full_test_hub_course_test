from django.urls import path, include
from src.common.api_views import (get_all_active_lesson_view, )
from src.common.api_views.lesson import import_question_from_test_hub_app
from src.quizzes.api_views import new_flash_card_view
from src.quizzes.api_views.flash_card import get_flash_card_question

api_v1_urlpatterns = [
    path('new-flash_card/', new_flash_card_view),
    path('flash_card-questions/', get_flash_card_question),
]

app_name = 'quizzes'
urlpatterns = [
    path('api/v1/', include(api_v1_urlpatterns)),
]
