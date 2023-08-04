from django.urls import path
# from rest_framework_simplejwt.views import TokenRefreshView

from src.accounts.api.views import (auth_me_view, get_token_view)

# from src.accounts.views import city_list
# from src.quizzes.api.views.students import StudentResultAvarageView

urlpatterns = [
    path('login/', get_token_view),
    path('me/', auth_me_view, name='auth_me'),
]
