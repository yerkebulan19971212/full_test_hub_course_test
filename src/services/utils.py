from __future__ import print_function

import base64
import email
import os.path
import re
import ast
import os
import time

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from datetime import datetime

from django.db.models import Sum, Q, Count
from django.db.models.functions import Coalesce

from src.common.send_kafka import send_to_kafka

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
MODIFY_SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def getenv_bool(name: str, default: str = "False"):
    raw = os.getenv(name, default).title()
    return ast.literal_eval(raw)


def finish_full_test(student_quizz_id: int):
    from src.quizzes.models import (TestFullScore, StudentQuizz, StudentScore,
                                    StudentQuizzQuestion)
    from src.common.models import CourseTypeLesson
    try:
        student_quizz = StudentQuizz.objects.get(pk=student_quizz_id)

        if not TestFullScore.objects.filter(
                student_quizz=student_quizz).exists():
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
                    Q(
                        Q(Q(question__student_quizz_questions__student_quizz=student_quizz),
                          Q(question__student_quizz_questions__lesson=lesson)) |
                        Q(Q(question__parent__student_quizz_questions__student_quizz=student_quizz),
                          Q(question__parent__student_quizz_questions__lesson=lesson))
                    ),
                    student_quizz=student_quizz,
                    lesson=lesson,
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
                            'question__lesson_question_level__question_level__point'),
                        0
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
                        accuracy=100 * score / question_full_score if question_full_score > 0 else 0
                    ))
            TestFullScore.objects.bulk_create(test_full_score)
            student_quizz.status = "PASSED"
            student_quizz.quizz_end_time = datetime.now()
            student_quizz.save()
    except Exception as e:
        print(e)


def get_result_st(student_quizz_id: int):
    from src.quizzes.models import (StudentQuizzQuestion, StudentScore,
                                    StudentAnswer, StudentQuizz, TestFullScore,
                                    Question)

    student_quizz = StudentQuizz.objects.get(pk=student_quizz_id)
    total_score = TestFullScore.objects.filter(
        student_quizz_id=student_quizz_id
    ).aggregate(total_score=Coalesce(Sum('score'), 0)).get("total_score")
    total_bal = Question.objects.filter(
        parent__isnull=True,
        student_quizz_questions__student_quizz_id=student_quizz_id,
    ).aggregate(
        sum_point=Coalesce(Sum('lesson_question_level__question_level__point'),
                           0)
    ).get('sum_point')
    answered_questions_parent_true = StudentAnswer.objects.filter(
        student_quizz=student_quizz_id,
        status=True,
        question__parent__isnull=True
    ).aggregate(
        answered_questions=Coalesce(Count('question_id', distinct=True), 0)
    ).get("answered_questions")

    answered_questions_parent_false = StudentAnswer.objects.filter(
        student_quizz=student_quizz_id,
        status=True,
        question__parent__isnull=False
    ).aggregate(
        answered_questions=Coalesce(
            Count('question__parent_id', distinct=True), 0)
    ).get("answered_questions")
    answered_questions = answered_questions_parent_true + answered_questions_parent_false
    quantity_correct_question_1 = StudentScore.objects.filter(
        student_quizz=student_quizz_id,
        question__parent__isnull=True,
        status=True,
        score__gt=0
    ).count()
    quantity_correct_question_2 = StudentScore.objects.filter(
        student_quizz=student_quizz_id,
        question__parent__isnull=False,
        status=True,
        score__gt=0
    ).values('question__parent').distinct().count()
    quantity_correct_question = quantity_correct_question_1 + quantity_correct_question_2
    quantity_question = StudentQuizzQuestion.objects.filter(
        student_quizz=student_quizz
    ).count()
    if answered_questions > 0:
        correct_question_percent = 100 * answered_questions / quantity_question
    else:
        correct_question_percent = 0
    return {
        "total_user_score": total_score,
        "total_score": total_bal,
        "start_time": student_quizz.quizz_start_time,
        "end_time": student_quizz.quizz_end_time,
        "duration": student_quizz.quizz_end_time - student_quizz.quizz_start_time,
        "quantity_question": quantity_question,
        "quantity_answered_questions": answered_questions,
        "quantity_correct_question": quantity_correct_question,
        "quantity_wrong_question": answered_questions - quantity_correct_question,
        "correct_question_percent": correct_question_percent,
    }


def create_question(questions_texts: str, variant_id: int, lesson_id: int, lql, v):
    from src.common import constant
    from src.quizzes.models import AnswerSign, Question, Answer, CommonQuestion
    if not questions_texts and 'new_line' not in questions_texts:
        return None
    answersign = AnswerSign.objects.all().order_by('id')

    questions_detail = questions_texts.split('new_line')
    question_text = ''
    choice = ''
    point = 1
    answer_start = 4
    index_plus = 0
    common_question = None
    question_type = constant.QuestionType.DEFAULT
    if "$SUB_QUESTION" in questions_texts and "$$SUB_QUESTION" in questions_texts:
        question_type = constant.QuestionType.SELECT
        answer_start += 2

    if questions_detail[0][0] == "*":
        common_question_text = questions_detail[0][1:].strip()
        common_question_query = CommonQuestion.objects.filter(
            text=common_question_text)
        if common_question_query.exists():
            common_question = common_question_query.first()
        else:
            common_question = CommonQuestion.objects.create(
                text=common_question_text)

        question_text = questions_detail[1][1:].strip()
        index_plus = 1
    elif questions_detail[0][0] == "#":
        answer_start -= 1
        question_text = questions_detail[0][1:].strip()

    if 'point' in questions_detail[1 + index_plus]:
        point = int(questions_detail[1 + index_plus].split(' ')[1].strip())
    if 'ch' in questions_detail[2 + index_plus]:
        choice = questions_detail[2 + index_plus].split(' ')[1]
    answers = questions_detail[answer_start:-2]
    if question_type == constant.QuestionType.DEFAULT:
        correct_answers = list(map(int, questions_detail[-2].split(',')))
        test_question = Question.objects.create(
            question=question_text,
            common_question=common_question,
            lesson_question_level=lql,
            variant_id=variant_id
        )
        Answer.objects.bulk_create([
            Answer(
                order=i,
                question=test_question,
                answer=ans.strip(),
                answer_sign=answersign[i],
                correct=True if (i + 1) in correct_answers else False
            ) for i, ans in enumerate(answers)
        ])
        return test_question
    else:
        correct_answers = list(map(int, questions_detail[-2].split(',')))
        test_question = Question.objects.create(
            question=question_text,
            common_question=common_question,
            question_type=constant.QuestionType.SELECT,
            variant_id=variant_id,
            lesson_question_level=lql,
        )
        question_text2 = questions_detail[answer_start - 2][
                         len("$SUB_QUESTION"):].strip()
        sub_question1 = Question.objects.create(
            parent=test_question,
            question=question_text2,
            question_type=constant.QuestionType.SELECT,
            variant_id=variant_id,
            lesson_question_level=lql,
        )
        question_text2 = questions_detail[answer_start - 1][
                         len("$$SUB_QUESTION"):].strip()
        sub_question2 = Question.objects.create(
            parent=test_question,
            question=question_text2,
            question_type=constant.QuestionType.SELECT,
            variant_id=variant_id,
            lesson_question_level=lql,
        )
        Answer.objects.bulk_create([
            Answer(
                order=i,
                question=sub_question1,
                answer=ans.strip(),
                answer_sign=answersign[i],
                correct=True if (i + 1) == correct_answers[0] else False
            ) for i, ans in enumerate(answers)
        ])
        Answer.objects.bulk_create([
            Answer(
                order=i,
                question=sub_question2,
                answer=ans.strip(),
                answer_sign=answersign[i],
                correct=True if (i + 1) == correct_answers[1] else False
            ) for i, ans in enumerate(answers)
        ])
        send_to_kafka("questions", {
            "question": {
                "questions_texts": questions_texts,
                "lesson_id": lesson_id,
                "lq": lql.id,
                "vaiant_code": v,
            },
            "type": "import"
        })

        return test_question
