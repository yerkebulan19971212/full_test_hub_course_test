from django.contrib import admin
from django.urls import path, include
# from .yasg import urlpatterns as doc_url
from django.conf import settings
from django.conf.urls.static import static
import debug_toolbar
from src.accounts.urls import urlpatterns as user_urlpatterns

api_v1_urlpatterns = [
    path('user/', include(user_urlpatterns)),
    # path('super-admin/', include(admin_urlpatterns)),
    # path('quizzes/', include(urlpatterns))
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_v1_urlpatterns)),
]

# urlpatterns += doc_url
if settings.DEBUG:
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
