import requests
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework import generics
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import \
    TokenObtainPairView as BaseTokenObtainPairView
from rest_framework import permissions

from src.accounts.api_views.serializers import (AuthMeSerializer,
                                                TokenObtainPairSerializer,
                                                RegisterPhoneSerializer,
                                                GoogleSerializer,
                                                RegisterEmailSerializer)
from src.accounts.models import Role
from src.common.exception import (UnexpectedError, PhoneExistError,
                                  EmailExistError)

User = get_user_model()


class AuthMeView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AuthMeSerializer
    queryset = User.objects.all()

    def get_object(self):
        user = self.request.user
        return user


auth_me_view = AuthMeView.as_view()


class RegisterStudentPhoneUserView(generics.CreateAPIView):
    serializer_class = RegisterPhoneSerializer

    def post(self, request, *args, **kwargs):
        phone = self.request.data.get("phone")
        user = User.objects.filter(phone=phone, role__name_code='student')
        if user.filter(is_active=True).exists():
            raise PhoneExistError()
        not_active_user = user.filter(is_active=False)
        if not_active_user.exists():
            not_active_user.delete()
        return self.create(request, *args, **kwargs)


register_phone_view = RegisterStudentPhoneUserView.as_view()


class RegisterStudentEmailUserView(generics.CreateAPIView):
    serializer_class = RegisterEmailSerializer

    def post(self, request, *args, **kwargs):
        email = self.request.data.get("email")
        user = User.objects.filter(email=email, role__name_code='student')
        if user.filter(is_active=True).exists():
            raise EmailExistError()
        not_active_user = user.filter(is_active=False)
        if not_active_user.exists():
            not_active_user.delete()
        return self.create(request, *args, **kwargs)


register_email_view = RegisterStudentEmailUserView.as_view()


class TokenObtainPairView(BaseTokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    # def post(self, request, *args, **kwargs):
    # phone = self.request.data.get('phone').lower()
    # user = User.objects.select_related('role').filter(phone=phone)
    # if not user.exists():
    #     return Response({"detail": "Такой пользователь не найден"},
    #                     status=status.HTTP_400_BAD_REQUEST)
    # user = user.first()
    # if not user.is_active:
    #     return Response({"detail": "Такой пользователь не найден"},
    #                     status=status.HTTP_400_BAD_REQUEST)
    # role = user.role
    # if role.name != "student":
    #     return Response({"detail": "Вы не студент"},
    #                     status=status.HTTP_400_BAD_REQUEST)
    # if not user.check_password(self.request.data.get('password')):
    #     return Response({"detail": "Неверный пароль"},
    #                     status=status.HTTP_400_BAD_REQUEST)
    #
    # return super().post(request, *args, **kwargs)


get_token_view = TokenObtainPairView.as_view()


class StaffTokenObtainPairView(BaseTokenObtainPairView):
    """ логин для сотрудников """
    serializer_class = TokenObtainPairSerializer


class GoogleJWTView(APIView):
    @swagger_auto_schema(request_body=GoogleSerializer)
    def post(self, request, *args, **kwargs):
        id_token = request.data.get('id_token', None)
        if not id_token:
            return None

        try:
            # Verify the JWT signature and extract the user ID and email
            response = requests.get(
                f'https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={id_token}')
            response.raise_for_status()
            user_data = response.json()
        except Exception as e:
            raise AuthenticationFailed('Failed to verify Google id_token')

        # Get or create user
        user, created = User.objects.get_or_create(
            email=user_data['email'])
        if created:
            user.username = user_data['email']
            user.first_name = user_data['given_name']
            user.last_name = user_data['family_name']
            user.role = Role.objects.filter(name_code='student').first()
            user.set_unusable_password()
            user.save()

        refresh = TokenObtainPairSerializer.get_token(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return Response(data, status=status.HTTP_200_OK)


google = GoogleJWTView.as_view()
