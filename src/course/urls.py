from django.urls import path, include

from src.course.api_views.views import (course_list_view, course_view, course_curriculum_view)

api_v1_urlpatterns = [
    path('all/', course_list_view),
    path('<uuid:uuid>/', course_view),
    path('curriculum/', course_curriculum_view),
]

app_name = 'course'
urlpatterns = [
    path('api/v1/', include(api_v1_urlpatterns)),
]
