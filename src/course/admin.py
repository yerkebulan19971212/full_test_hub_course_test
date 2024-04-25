from django.contrib import admin
from .models import (Course, CLesson, CourseLessonType, CourseTopicLesson,
                     Category, CourseTopic, Topic, UserCLesson, UserCourse)

admin.site.register([
    UserCourse,
    Course,
    CLesson,
    CourseTopicLesson,
    CourseTopic,
    Topic,
    CourseLessonType,
    UserCLesson,
    Category
])
