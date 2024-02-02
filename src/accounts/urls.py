from django.urls import path, include
from src.accounts.api_views.views import (auth_me_view, token_by_phone_view,
                                          token_by_email_view,
                                          register_email_view, google,
                                          register_phone_view,
                                          token_staff_view,
                                          update_password_view,
                                          update_profile_view,
                                          update_login_profile_view,
                                          update_google_password_view,
                                          profile_view, admin_update_password_view, user_list_view, add_balance_history)

app_name = 'accounts'
urlpatterns = [
    path('login-phone/', token_by_phone_view),
    path('login-email/', token_by_email_view),
    path('login-staff/', token_staff_view),
    path('register-phone/', register_phone_view),
    path('register-email/', register_email_view),
    path('google/', google),
    path('me/', auth_me_view),

    path('change-password/', update_password_view),
    path('google/password/', update_google_password_view),
    path('profile/', profile_view),
    path('update-profile/', update_profile_view),
    path('update-login/', update_login_profile_view),
]

accounts_api_v1_urlpatterns = [
    path('api/v1/', include(urlpatterns)),
    # path('super-admin/', include(admin_urlpatterns)),
    # path('quizzes/', include(urlpatterns))
]

super_admin_api_v1_urlpatterns = [
    path('staff-login/', token_staff_view),
    path('me/', auth_me_view),
    path('password/', admin_update_password_view),
    path('add-balance/', add_balance_history),

]
