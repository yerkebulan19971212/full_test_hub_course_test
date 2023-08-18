from django.urls import path, include
# from rest_framework_simplejwt.views import TokenRefreshView

from src.common.api_views import (get_all_active_lesson_view, )

# from src.accounts.views import city_list
# from src.quizzes.api_views.views.students import StudentResultAvarageView

app_name = 'common'
urlpatterns = [
    path('login/', get_all_active_lesson_view),
]
api_v1_urlpatterns = [
    path('api/v1/', include(urlpatterns)),
    # path('super-admin/', include(admin_urlpatterns)),
    # path('quizzes/', include(urlpatterns))
]
