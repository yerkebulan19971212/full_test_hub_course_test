from .by_lesson import (by_lesson_finish_view, by_lesson_pass_answer_view,
                        by_lesson_quizz_lesson_view,
                        by_lesson_quizz_question_view, by_lesson_quizz_view,
                        new_by_lesson_quizz_view, by_lesson_result_view,
                        get_by_lesson_result_question,
                        get_by_lesson_full_score_result_view,
                        by_lesson_result_task_progress_view)
from .flash_card import get_flash_card_question, new_flash_card_view
from .full_test import (full_quizz_lesson_view, full_quizz_question_view,
                        full_quizz_view, full_test_finish_view, my_test_view,
                        get_result_question, get_files_view,
                        get_full_test_full_score_result_view,
                        new_full_test_view, pass_answer_view, st_result_view)
from .quiz_test import (finish_quiz_test, get_quiz_test_question_view,
                        new_quizz_test_view, pass_quizz_test_answer_view,
                        quiz_test_check_answer_view)
