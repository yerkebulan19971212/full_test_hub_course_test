from django.urls import path, include
from src.accounts.api_views.views import (auth_me_view, token_by_phone_view,
                                          token_by_email_view,
                                          register_email_view, google,
                                          register_phone_view, token_staff_view)

app_name = 'accounts'
urlpatterns = [
    path('login-phone/', token_by_phone_view),
    path('login-email/', token_by_email_view),
    path('login-staff/', token_staff_view),
    path('register-phone/', register_phone_view),
    path('register-email/', register_email_view),
    path('google/', google),
    path('me/', auth_me_view, name='auth_me'),
]

accounts_api_v1_urlpatterns = [
    path('api/v1/', include(urlpatterns)),
    # path('super-admin/', include(admin_urlpatterns)),
    # path('quizzes/', include(urlpatterns))
]
