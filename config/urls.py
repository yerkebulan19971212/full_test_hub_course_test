from django.contrib import admin
from django.urls import path, include
# from .yasg import urlpatterns as doc_url
from django.conf import settings
from django.conf.urls.static import static
import debug_toolbar
from src.accounts.urls import accounts_api_v1_urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include(accounts_api_v1_urlpatterns)),
]

# urlpatterns += doc_url
if settings.DEBUG:
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
