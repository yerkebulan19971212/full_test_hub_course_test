from django.contrib import admin
from django.urls import path, include
from config.yasg import urlpatterns as doc_url
from django.conf import settings
from django.conf.urls.static import static
import debug_toolbar
from src.accounts.urls import accounts_api_v1_urlpatterns
from src.common.urls import api_v1_urlpatterns as common_url,api_v1_quizzes, api_v1_super_admin_urlpatterns
from src.quizzes.urls import urlpatterns as quizzes_url
from src.accounts.urls import super_admin_api_v1_urlpatterns
from src.services.views import utils_v

urlpatterns = [
    path('api/v1/super-admin/', include(api_v1_super_admin_urlpatterns)),
    path('api/v1/quizzes/', include(api_v1_quizzes)),
    path('api/v1/user/', include(super_admin_api_v1_urlpatterns)),
    path('util/', utils_v),
    path('admin/', admin.site.urls),
    path('accounts/',
         include((accounts_api_v1_urlpatterns, 'accounts'),
                 namespace='accounts')),
    path('commmon/', include((common_url, 'common'), namespace='common')),
    path('quizzes/',
         include((quizzes_url, 'quizzes'), namespace='quizzes')),
]

urlpatterns += doc_url
if settings.DEBUG:
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
