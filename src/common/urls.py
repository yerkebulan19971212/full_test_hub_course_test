from django.urls import path, include

from src.common.api_views import (get_all_active_lesson_view, packet_view,
                                  lesson_pair_list_view, quizz_types_view,
                                  get_all_cities_view, get_all_school_view,
                                  buy_packet_view,
                                  get_all_active_lesson_with_pairs_view,
                                  get_all_rating_test_view, promo_code_view)
from src.common.api_views.lesson import import_question_from_test_hub_app
from src.common.super_admin_views import (
    variant_list,
    variant_lesson_view,
    import_question_view,
    check_add_question_view, common_question_list_view, add_question_view, question_list_view
)
from src.common.views import support_view

app_name = 'common'

urlpatterns = [
    path('promotion/promo-code/', promo_code_view),
    path('support/', support_view),
    path('lessons/', get_all_active_lesson_view),
    path('import-q/', import_question_from_test_hub_app),
    path('lesson-pairs/', lesson_pair_list_view),
    path('quizz-types/', quizz_types_view),
    path('packet-list/', packet_view),
    path('rating-test-list/', get_all_rating_test_view),
    path('buy-packet/', buy_packet_view),
    path('schools/', get_all_school_view),
    path('cities/', get_all_cities_view),
    path('lessons-with-pairs/', get_all_active_lesson_with_pairs_view),
]
api_v1_urlpatterns = [
    path('api/v1/', include(urlpatterns)),
]

api_v1_super_admin_urlpatterns = [
    path('add-question/', add_question_view),
    path('variant-list/', variant_list),
    path('common-question-list/<int:variant_id>/', common_question_list_view),
    path('variant-lessons/<int:variant_id>/', variant_lesson_view),
    path('check-variant/<int:variant_id>/<int:lesson_id>/', check_add_question_view),
    path('question-list/<int:variant_id>/<int:lesson_id>/', question_list_view),
    path('add/<int:variant_id>/<int:lesson_id>/', import_question_view),
]
