from datetime import datetime, timedelta


def get_correct_answer_count(a, b):
    result = list(filter(lambda x: x in a, b))
    return len(result)


def get_multi_score(correct_p, answer_p):
    correct_p = [ans.id for ans in correct_p]
    answer_p = [ans.id for ans in answer_p]
    correct_answer_count = get_correct_answer_count(correct_p, answer_p)
    if len(correct_p) == 1 and correct_answer_count == 1:
        if len(answer_p) == 1:
            return 2
        elif len(answer_p) == 2:
            return 1
    elif len(correct_p) != 1:
        if len(correct_p) == len(answer_p) == correct_answer_count:
            return 2
        elif (len(answer_p) == len(
                correct_p) - 1 and correct_answer_count == len(
            correct_p) - 1) or (
                len(answer_p) == len(
            correct_p) + 1 and correct_answer_count == len(correct_p)):
            return 1
        elif ((len(correct_p) == len(answer_p)) or len(correct_p) == (
                len(answer_p))) and (
                correct_answer_count == len(correct_p) - 1):
            return 1
    return 0


def get_monday_and_next_monday():
    current_date = datetime.now()
    days_to_monday = current_date.weekday() - 0  # Monday is represented by 0 in Python's datetime module
    monday = current_date - timedelta(days=days_to_monday)
    next_monday = monday + timedelta(days=6)
    return monday.date(), next_monday.date()
