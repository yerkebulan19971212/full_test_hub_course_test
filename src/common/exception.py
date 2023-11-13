from rest_framework import serializers, status

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException


class UnexpectedError(APIException):
    message = _("server error")
    default_code = _("server_error")


class ServerError(APIException):
    message = _("server error")
    default_code = _("server_error")


class UserNotExistError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = _("user_not_exist")
    default_detail = _("user not exist")
    default_code = "user_not_exist"


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


class IsNotStudentError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("is not student")
    default_code = "is_not_student"


class IsNotStaffError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("is not staff")
    default_code = "is_not_staff"


class PasswordNotCorrectError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("password not correct")
    default_code = "password_not_correct"


class EmailAlreadyExistError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("email already exist error")
    default_code = "email_already_exist_error"


class PhoneAlreadyExistError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("phone already exist error")
    default_code = "phone_already_exist_error"


class PasswordsDoNotMatchError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("passwords do not match error")
    default_code = "passwords_not_match_error"


class AccountDoesNotHavePasswordError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("account does not have password error")
    default_code = "not_password_error"
