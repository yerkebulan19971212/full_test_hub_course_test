from django.urls import path, include
# from rest_framework_simplejwt.views import TokenRefreshView

from src.common.api_views import (get_all_active_lesson_view, packet_view,
                                  lesson_pair_list_view, quizz_types_view,
                                  buy_packet_view, get_all_active_lesson_with_pairs_view)
from src.common.api_views.lesson import import_question_from_test_hub_app

# from src.accounts.views import city_list
# from src.quizzes.api_views.views.students import StudentResultAvarageView

app_name = 'common'
# quizz_urlpatterns = [
#     path()
# ]
urlpatterns = [
    path('lessons/', get_all_active_lesson_view),
    path('import-q/', import_question_from_test_hub_app),
    path('lesson-pairs/', lesson_pair_list_view),
    path('quizz-types/', quizz_types_view),
    path('packet-list/', packet_view),
    path('buy-packet/', buy_packet_view),
    path('lessons-with-pairs/', get_all_active_lesson_with_pairs_view),
]
api_v1_urlpatterns = [
    path('api/v1/', include(urlpatterns)),
    # path('super-admin/', include(admin_urlpatterns)),
    # path('quizzes/', include(urlpatterns))
]
