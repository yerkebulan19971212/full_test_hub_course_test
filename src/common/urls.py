from django.urls import path, include
# from rest_framework_simplejwt.views import TokenRefreshView

from src.common.api_views import (get_all_active_lesson_view, lesson_pair_list_view)
from src.common.api_views.lesson import import_question_from_test_hub_app

# from src.accounts.views import city_list
# from src.quizzes.api_views.views.students import StudentResultAvarageView

app_name = 'common'
urlpatterns = [
    path('login/', get_all_active_lesson_view),
    path('import-q/', import_question_from_test_hub_app),
    path('lesson-pairs/', lesson_pair_list_view),
]
api_v1_urlpatterns = [
    path('api/v1/', include(urlpatterns)),
    # path('super-admin/', include(admin_urlpatterns)),
    # path('quizzes/', include(urlpatterns))
]
