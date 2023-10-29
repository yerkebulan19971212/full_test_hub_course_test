from rest_framework import serializers, status

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException


class UnexpectedError(APIException):
    message = _("server error")
    default_code = _("server_error")


class ServerError(APIException):
    message = _("server error")
    default_code = _("server_error")


class PhoneExistError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = _("phone_exist")
    default_detail = _("Phone exist")
    default_code = "phone_exist"


class EmailExistError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = _("email_exist")
    default_detail = _("email exist")
    default_code = "email_exist"
