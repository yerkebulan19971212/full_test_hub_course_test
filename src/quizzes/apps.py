from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class QuizzesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.quizzes'
    verbose_name = _("Quizzes")
