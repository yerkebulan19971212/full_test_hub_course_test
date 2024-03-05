from __future__ import print_function

import base64
import email
import os.path
import re
import requests
import ast
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from datetime import datetime

from django.db.models import Sum, Q, F
from django.db.models.functions import Coalesce

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
MODIFY_SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def getenv_bool(name: str, default: str = "False"):
    raw = os.getenv(name, default).title()
    return ast.literal_eval(raw)


def finish_full_test(student_quizz_id: int):
    from src.quizzes.models import (TestFullScore, StudentQuizz, StudentScore, StudentQuizzQuestion)
    from src.common.models import CourseTypeLesson
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
                print(lesson)
                index += 1
                question_score = StudentScore.objects.filter(
                    Q(
                        Q(Q(question__student_quizz_questions__student_quizz=student_quizz),
                          Q(question__student_quizz_questions__lesson=lesson)) |
                        Q(Q(question__parent__student_quizz_questions__student_quizz=student_quizz),
                          Q(question__parent__student_quizz_questions__lesson=lesson))
                    ),
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
                        accuracy=100 * score / question_full_score if question_full_score > 0 else 0
                    ))
            TestFullScore.objects.bulk_create(test_full_score)
    except Exception as e:
        print(e)


def create_question(questions_texts: str, variant_id: int, lesson_id: int, lql):
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

        return test_question


def get_message(service, user_id, msg_id):
    msg = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
    msg_raw = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
    msg_str = email.message_from_bytes(msg_raw)
    content_types = msg_str.get_content_maintype()
    if content_types == 'multipart':
        part1, part2 = msg_str.get_payload()
        body_text = str(part1).split("\n\n")[-1]
    else:
        body_text = str(msg_str.get_payload())
    sample_string_bytes = base64.b64decode(body_text)
    sample_string = sample_string_bytes.decode("utf-8")
    return sample_string


def as_read_message(msg_id):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', MODIFY_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', MODIFY_SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)

    msg = service.users().messages().modify(userId='me', id=msg_id, body={"removeLabelIds": ["UNREAD"]}).execute()


def add_balance():
    from src.accounts.models import BalanceHistory, User

    creds = None
    if os.path.exists('read_token.json'):
        creds = Credentials.from_authorized_user_file('read_token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('read_token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        q="from:kaspi.payments@kaspibank.kz is:unread"
    ).execute()
    messages = results.get('messages', [])
    if not messages:
        print("You have no new messages.")
    else:
        print("message")

        for message in messages:
            msg = get_message(
                service=service,
                user_id='me',
                msg_id=message['id']
            )
            id_msg = re.search(r"= \d\d\d\d\d\d", msg)
            price_msg = re.search(r"у: \d+\.\d+", msg)
            if id_msg is None:
                continue
            user_id = id_msg.group(0).split(' ')[-1].strip()
            price = str(price_msg.group(0)).split(' ')[-1].strip()
            user = User.objects.filter(user_id=int(user_id)).first()
            if user is not None:
                BalanceHistory.objects.create(
                    student=user,
                    balance=int(float(price)),
                    data=msg
                )
            as_read_message(message['id'])
    if not messages:
        print('No messages found')
