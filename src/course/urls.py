from django.urls import path, include

from src.course.api_views.admin import topic_retrieve_update_view
from src.course.api_views.views import (course_list_view, course_view,
                                        course_curriculum_view,
                                        course_curriculum_user_view,
                                        course_lesson_user_view)
from src.course.api_views import (category_list_view,
                                  course_create_view,
                                  admin_course_list_view,
                                  admin_course_retrieve_update_destroy_view,
                                  topic_create_view, c_lesson_type_list_view,
                                  retrieve_update_destroy_lesson_view,
                                  admin_course_topic_list_view,
                                  c_lesson_create_view)

admin_urlpatterns = [
    path('category/all/', category_list_view),
    path('course/', course_create_view),
    path('course/all/', admin_course_list_view),
    path('course/<int:pk>/', admin_course_retrieve_update_destroy_view),

    path('lesson/', c_lesson_create_view),
    path('lesson/<uuid:uuid>/', retrieve_update_destroy_lesson_view),
    path('section/<uuid:uuid>/', topic_retrieve_update_view),
    path('section/', topic_create_view),
    path('section/all/', admin_course_topic_list_view),
    path('lesson-types/', c_lesson_type_list_view),

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
