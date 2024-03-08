from django.db.models import Subquery, Q, OuterRef, Exists, F, Sum
from django.db.models.functions import Coalesce

from src.common import constant
from src.quizzes.models import Question, StudentScore, StudentAnswer


def get_result_lesson(student_quizz_id: int, data):
    for d in data:
        questions = Question.objects.filter(
            student_quizz_questions__student_quizz_id=student_quizz_id,
            student_quizz_questions__lesson_id=d.get('lesson_id'),
            parent__isnull=True
        ).annotate(
            answered_correct=Subquery(
                StudentScore.objects.filter(
                    Q(
                        status=True,
                        student_quizz_id=student_quizz_id,
                        score__gt=0
                    ) & Q(
                        Q(question__parent_id=OuterRef('pk'))
                        | Q(question_id=OuterRef('pk'))
                    )
                ).values('question__parent_id').annotate(sum_score=Coalesce(Sum('score'), 0)).values('sum_score')[:1]),
            point=F('lesson_question_level__question_level__point'),
            answered=Exists(
                StudentAnswer.objects.filter(
                    Q(
                        student_quizz_id=student_quizz_id,
                        status=True
                    ) & Q(
                        Q(question__parent_id=OuterRef('pk'))
                        | Q(question_id=OuterRef('pk'))
                    )
                ))
        ).order_by('student_quizz_questions__order')
        d['questions'] = []
        for q in questions:
            answered = constant.AnswerStatus.NOT_ANSWERED
            if q.answered:
                if q.answered_correct is None:
                    answered = constant.AnswerStatus.WRONG
                else:
                    if 0 < q.answered_correct == q.point:
                        answered = constant.AnswerStatus.CORRECT
                    elif 0 < q.answered_correct < q.point:
                        answered = constant.AnswerStatus.HALF_CORRECT
            d['questions'].append({
                "question_id": q.id,
                "correct_answered": answered,
            })
    data = [d for d in data if len(d.get("questions")) > 0]
    return data
