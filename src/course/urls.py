from django.urls import path, include

from src.course.api_views.views import (course_list_view, course_view,
                                        course_curriculum_view,
                                        course_curriculum_user_view,
                                        course_lesson_user_view)
from src.course.api_views import (category_list_view,
                                  course_create_view,
                                  admin_course_list_view,
                                  admin_course_retrieve_update_destroy_view)

admin_urlpatterns = [
    path('category/all/', category_list_view),
    path('course/', course_create_view),
    path('course/all/', admin_course_list_view),
    path('course/<uuid:uuid>/', admin_course_retrieve_update_destroy_view),

]

api_v1_urlpatterns = [
    path('admin/', include(admin_urlpatterns)),
    path('all/', course_list_view),
    path('<uuid:uuid>/', course_view),
    path('curriculum/', course_curriculum_view),
    path('curriculum-user/', course_curriculum_user_view),
    path('lesson/', course_lesson_user_view),
]

app_name = 'course'
urlpatterns = [
    path('api/v1/', include(api_v1_urlpatterns)),
]
