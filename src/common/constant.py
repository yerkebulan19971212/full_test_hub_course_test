from enum import Enum

from django.utils.translation import gettext_lazy as _


class Choice(Enum):
    @classmethod
    def choices(cls):
        return [(c.value, _(c.name)) for c in cls]

    @classmethod
    def repr(cls):
        return {c.name: {'id': c.value, 'name': _(c.name)} for c in cls}

    @classmethod
    def list(cls):
        return [c.value for c in cls]

    def __str__(self):
        return self.value


class Role(str, Choice):
    SUPER_ADMIN = 'SUPER_ADMIN'
    TEACHER = 'TEACHER'
    CURATOR = 'CURATOR'
    STUDENT = 'STUDENT'


class TestLang(str, Choice):
    KAZAKH = 'kz'
    RUSSIAN = 'ru'


class QuizzType(str, Choice):
    BY_LESSON = 'BY_LESSON'
    FLASH_CARD = 'FLASH_CARD'
    FULL_TEST_ENT = 'FULL_TEST_ENT'
    INFINITY_QUIZ = 'INFINITY_QUIZ'


class PacketType(str, Choice):
    ONE_TIME = 'ONE_TIME'
    MANY_TIMES = 'MANY_TIMES'


class Status(str, Choice):
    NOT_PASSED = 'NOT_PASSED'
    CONTINUE = 'CONTINUE'
    PASSED = 'PASSED'


class ChoiceType(int, Choice):
    CHOICE = 0
    MULTI_CHOICE = 1


class GradeType(int, Choice):
    VERY_BAD = 1
    BAD = 2
    AVERAGE = 3
    GOOD = 4
    EXCELLENT = 5


class ErrorType(int, Choice):
    GRADE = 1
    COMPLAIN = 2


class FavoriteType(str, Choice):
    TEST = 'TEST'
    SEARCH = 'SEARCH'
    FLASH_CARD = 'FLASH_CARD'


class UniversityStatus(str, Choice):
    NATIONAL = 'TEST'


class QuizzStatus(str, Choice):
    NOT_PASSED = 'NOT_PASSED'
    CONTINUE = 'CONTINUE'
    PASSED = 'PASSED'
    EXPIRED = 'EXPIRED'


class CourseStatus(str, Choice):
    NOT_PASSED = 'NOT_PASSED'
    CONTINUE = 'CONTINUE'
    PASSED = 'PASSED'
    EXPIRED = 'EXPIRED'


class AnswerStatus(str, Choice):
    NOT_ANSWERED = 'NOT_ANSWERED'
    CORRECT = 'CORRECT'
    WRONG = 'WRONG'
    HALF_CORRECT = 'HALF_CORRECT'


class QuestionType(str, Choice):
    DEFAULT = 'DEFAULT'
    SELECT = 'SELECT'


class PromoCodeType(str, Choice):
    ORDINARY = 'ORDINARY'
    TELEGRAM = 'TELEGRAM'
