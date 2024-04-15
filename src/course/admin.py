from django.contrib import admin
from .models import (Course, CLesson, CourseLessonType, CourseTopicLesson,
                     Category, CourseTopic, Topic, UserCLesson)

admin.site.register([
    Course,
    CLesson,
    CourseTopicLesson,
    CourseTopic,
    Topic,
    CourseLessonType,
    UserCLesson,
    Category
])
