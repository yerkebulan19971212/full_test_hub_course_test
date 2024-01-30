import ast

import os
from datetime import datetime

from django.db.models import Sum
from django.db.models.functions import Coalesce

from src.quizzes.models import (TestFullScore, StudentQuizz, StudentScore, StudentQuizzQuestion)
from src.common.models import CourseTypeLesson


def getenv_bool(name: str, default: str = "False"):
    raw = os.getenv(name, default).title()
    return ast.literal_eval(raw)


def finish_full_test(student_quizz_id: int):
    try:
        student_quizz = StudentQuizz.objects.get(pk=student_quizz_id)
        test_full_score = TestFullScore.objects.filter(student_quizz=student_quizz)
        if not test_full_score.exists():
            student_quizz.status = "PASSED"
            student_quizz.quizz_end_time = datetime.now()
            student_quizz.save()
            if student_quizz.lesson_pair:
                test_type_lessons = CourseTypeLesson.objects.filter(
                    main=True, course_type__name_code='ent'
                )
                lessons = [test_type_lesson.lesson for test_type_lesson in
                           test_type_lessons]
                lesson_pair = student_quizz.lesson_pair
                lessons.append(lesson_pair.lesson_1)
                lessons.append(lesson_pair.lesson_2)
            else:
                lessons = [student_quizz.lesson]
            index = 0
            test_full_score = []
            for lesson in lessons:
                index += 1
                question_score = StudentScore.objects.filter(
                    question__student_quizz_questions__lesson=lesson,
                    student_quizz=student_quizz,
                    status=True
                ).distinct().aggregate(sum_score=Coalesce(Sum('score'), 0))
                quantity_question = StudentQuizzQuestion.objects.filter(
                    student_quizz=student_quizz,
                    lesson=lesson
                ).count()
                question_full_score = StudentQuizzQuestion.objects.filter(
                    student_quizz=student_quizz,
                    question__parent__isnull=True,
                    lesson=lesson
                ).distinct().aggregate(
                    sum_score=Coalesce(
                        Sum(
                            'question__lesson_question_level__question_level__point'), 0
                    )
                ).get("sum_score")
                score = question_score.get('sum_score', 0)
                test_full_score.append(
                    TestFullScore(
                        student_quizz=student_quizz,
                        lesson=lesson,
                        score=score,
                        unattem=quantity_question - score,
                        number_of_score=question_full_score,
                        number_of_question=quantity_question,
                        accuracy=100 * score / question_full_score
                    ))
            TestFullScore.objects.bulk_create(test_full_score)
    except Exception as e:
        print(e)
