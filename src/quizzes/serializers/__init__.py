from .flash_card import FlashCardQuizzSerializer, FlashCardQuestionSerializer
from .answer import AnswerSerializer
from .question import (QuestionSerializer, FullQuizQuestionSerializer,
                       ResultScoreSerializer, TestFullScoreSerializer)
from .quizz_test import (QuizzTestSerializer, QuizTestPassAnswerSerializer)
from .full_test import (FullQuizzSerializer, StudentQuizzInformationSerializer,
                        FullQuizLessonListSerializer, StudentAnswersSerializer)
from .common import MyTestSerializer
from .student_quizz import ByLessonQuizzSerializer
