from rest_framework import serializers, status

from django.utils.translation import gettext_lazy as _


class UnexpectedError(Exception):
    message = _("unexpected error")
