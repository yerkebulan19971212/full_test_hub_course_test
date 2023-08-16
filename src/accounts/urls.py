from django.urls import path, include
# from rest_framework_simplejwt.views import TokenRefreshView

from src.accounts.api.views import (auth_me_view, get_token_view)

# from src.accounts.views import city_list
# from src.quizzes.api.views.students import StudentResultAvarageView

urlpatterns = [
    path('login/', get_token_view),
    path('me/', auth_me_view, name='auth_me'),
]


accounts_api_v1_urlpatterns = [
    path('api/v1/', include(urlpatterns)),
    # path('super-admin/', include(admin_urlpatterns)),
    # path('quizzes/', include(urlpatterns))
]
