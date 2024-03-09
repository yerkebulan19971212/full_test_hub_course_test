from django.urls import path, include

from src.course.api_views.views import course_list_view

api_v1_urlpatterns = [
    path('all/', course_list_view),
]

app_name = 'course'
urlpatterns = [
    path('api/v1/', include(api_v1_urlpatterns)),
]
