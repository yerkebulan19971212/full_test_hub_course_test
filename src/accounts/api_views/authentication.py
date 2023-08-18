from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication

from src.accounts.models import TokenVersion

UserModel = get_user_model()


class EmailAuthBackend(ModelBackend):
    """
    Authenticate using e-mail account.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):

        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password)\
                    and self.user_can_authenticate(user):
                return user
        return None

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None


class OwnJWTAuthentication(JWTAuthentication):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in a request header.
    """
    www_authenticate_realm = 'api_views'

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        version = validated_token['version']
        user_id = validated_token['user_id']
        token_version = TokenVersion.objects.filter(user_id=user_id)
        if token_version:
            if version != token_version.first().version:
                raise AuthenticationFailed(
                    _('Authorization header must contain two space-delimited values'),
                    code='bad_authorization_header',
                )
        else:
            raise AuthenticationFailed(
                _('Authorization header must contain two space-delimited values'),
                code='bad_authorization_header',
            )

        return self.get_user(validated_token), validated_token