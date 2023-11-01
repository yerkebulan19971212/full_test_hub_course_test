from django.urls import path, include
from src.accounts.api_views.views import (auth_me_view, token_by_phone_view,
                                          token_by_email_view,
                                          register_email_view, google,
                                          register_phone_view,
                                          token_staff_view,
                                          update_password_view,
                                          update_profile_view,
                                          profile_view)

app_name = 'accounts'
urlpatterns = [
    path('login-phone/', token_by_phone_view),
    path('login-email/', token_by_email_view),
    path('login-staff/', token_staff_view),
    path('register-phone/', register_phone_view),
    path('register-email/', register_email_view),
    path('google/', google),
    path('me/', auth_me_view, name='auth_me'),
    path('change-password/', update_password_view, name='update_password'),
    path('profile/', profile_view, name='profile'),
    path('update-profile/', update_profile_view, name='update_profile'),
]

accounts_api_v1_urlpatterns = [
    path('api/v1/', include(urlpatterns)),
    # path('super-admin/', include(admin_urlpatterns)),
    # path('quizzes/', include(urlpatterns))
]
