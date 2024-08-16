from django.urls import include, path

from src.accounts.api_views.views import user_list_view
from src.common.api_views import (buy_packet_view, get_all_active_lesson_view,
                                  get_all_active_lesson_with_pairs_view,
                                  get_all_cities_view,
                                  get_all_rating_test_view,
                                  get_all_school_view, lesson_pair_list_view,
                                  packet_view, promo_code_view,
                                  quizz_types_view, blog_list_view, blog_detail_view, blog_recommendation_view,
                                  packet_one_view)
from src.common.api_views.lesson import import_question_from_test_hub_app
from src.common.super_admin_views import (add_question_view,
                                          check_add_question_view,
                                          common_question_list_view,
                                          get_update_destroy_question_view,
                                          import_question_view,
                                          question_level_list_view,
                                          question_list_view, save_image_view,
                                          variant_lesson_view, variant_list, create_variant_view, student_detail,
                                          student_detail_update, destroy_variant, add_common_question_view,
                                          get_update_common_view, question_items_list_view)
from src.common.views import support_view, create_token_view, create_read_token_view

app_name = 'common'
urlpatterns = [
    path('create-read-token', create_read_token_view),
    path('create-token/', create_token_view),
    path('promotion/promo-code/', promo_code_view),
    path('support/', support_view),
    path('lessons/', get_all_active_lesson_view),
    path('import-q/', import_question_from_test_hub_app),
    path('lesson-pairs/', lesson_pair_list_view),
    path('quizz-types/', quizz_types_view),
    path('packet-list/', packet_view),
    path('packet/<uuid:uuid>/', packet_one_view),
    path('rating-test-list/', get_all_rating_test_view),
    path('buy-packet/', buy_packet_view),
    path('schools/', get_all_school_view),
    path('cities/', get_all_cities_view),
    path('lessons-with-pairs/', get_all_active_lesson_with_pairs_view),
    path('blog/all/',  blog_list_view),
    path('blog/<uuid:uuid>/', blog_detail_view),
    path('blog/recommendation/<uuid:uuid>', blog_recommendation_view),
]

api_v1_urlpatterns = [
    path('api/v1/', include(urlpatterns)),
]

api_v1_super_admin_urlpatterns = [
    path('get-all-students/', user_list_view),
    path('create-variant/', create_variant_view),
    path('destroy-variant/<int:pk>/', destroy_variant),
    path('add-question/', add_question_view),
    path('variant-list/', variant_list),
    path('question-level/', question_level_list_view),
    path('common-question-list/<int:variant_id>/', common_question_list_view),
    path('common-question/<int:pk>/', get_update_common_view),
    path('variant-lessons/<int:variant_id>/', variant_lesson_view),
    path('question/<int:pk>/', get_update_destroy_question_view),
    path('check-variant/<int:variant_id>/<int:lesson_id>/', check_add_question_view),
    path('question-list/<int:variant_id>/<int:lesson_id>/', question_list_view),
    path('question-items/<int:variant_id>/<int:lesson_id>/', question_items_list_view),
    path('add-question/<int:variant_id>/<int:lesson_id>/', import_question_view),
    path('student/<int:pk>/', student_detail),
    path('student-update/<int:pk>/', student_detail_update),
    path('add-common-question/', add_common_question_view),
]
api_v1_quizzes = [
    path('question-image/', save_image_view),
]
