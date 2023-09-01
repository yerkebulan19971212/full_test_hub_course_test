import secrets
import string
import requests
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max, Count
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework import generics
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import \
    TokenObtainPairView as BaseTokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters

# from src.base.paginations import StudentPagination
# from src.base.permissions import SuperAdminPermission, TeacherPermission
# from src.base.services import send_sms
from src.accounts.api_views.serializers import (AuthMeSerializer,
                                                TokenObtainPairSerializer,
                                                RegisterSerializer,
                                                StudentLessonSerializer,
                                                AddTeacherSerializer,
                                                CuratorSerializer,
                                                CreateStudentSerializer,
                                                GetTeacherSerializer,
                                                UserChangePasswordSerializer,
                                                SendPasswordToEmailSerializer,
                                                ValidateOtpSerializer,
                                                GoogleSerializer)
from src.accounts.models import Role
from src.common.exception import UnexpectedError

# from src.oauth.models import UserGeneratePassword, StudentLesson, \
#     PhoneOtp

User = get_user_model()


class AuthMeView(generics.RetrieveAPIView):
    serializer_class = AuthMeSerializer
    queryset = User.objects.all()

    def get_object(self):
        user = self.request.user
        return user


auth_me_view = AuthMeView.as_view()


class RegisterStudentUserView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        phone = self.request.data.get('phone')
        if phone:
            phone = phone.lower()
        user = User.objects.filter(
            phone=phone,
            role__name_code='student'
        )

        if user.filter(is_active=True).exists():
            raise UnexpectedError()
            return Response(
                {'detail': 'Такой пользователь уже существует'},
                status=status.HTTP_400_BAD_REQUEST
            )
        not_active_user = user.filter(is_active=False)
        if not_active_user.exists():
            not_active_user.delete()
        return self.create(request, *args, **kwargs)


register_view = RegisterStudentUserView.as_view()


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

    # def post(self, request, *args, **kwargs):
    #     phone = self.request.data.get('phone')
    #     user = User.objects.filter(phone=phone)
    #     if user:
    #         user = user.first()
    #     else:
    #         return Response({"detail": "Такой пользователь не найден"},
    #                         status=status.HTTP_400_BAD_REQUEST)
    #     role = user.role
    #     if role:
    #         if role.name == 'student':
    #             return Response({"detail": "student"},
    #                             status=status.HTTP_400_BAD_REQUEST)
    #     else:
    #         return Response({"detail": "role net"},
    #                         status=status.HTTP_400_BAD_REQUEST)
    #
    #     return super().post(request, *args, **kwargs)


# class GenerateOTPView(CreateAPIView):
#     serializer_class = PhoneOtpSerializer
#
#     def post(self, request, *args, **kwargs):
#         phone = self.request.data.get('phone')
#         forgot = self.request.data.get('forgot', False)
#         phone_opt = PhoneOtp.create_otp_for_phone(phone=phone, forgot=forgot)
#         text = "Juz40test.kz код для подтверждения - " + str(phone_opt.otp)
#         if forgot:
#             text = "Juz40test.kz код для подтверждения - " + str(phone_opt.otp)
#         send = send_sms(phone, text)
#         if send.get('code') != 0:
#             return Response({"error": send.get('data').get(
#                 'recipient') + send.get('message')}, status=400)
#         return Response({"status": "Сообшение успешно отправлено"}, status=200)
#
#
# generate_otp = GenerateOTPView.as_view()
#
#
# class ValidateOTPView(CreateAPIView):
#     serializer_class = ValidateOtpSerializer
#
#     def post(self, request, *args, **kwargs):
#         phone = self.request.data.get('phone')
#         otp = self.request.data.get('otp')
#         phone_otp = PhoneOtp.objects.filter(phone=phone).last()
#         if otp == phone_otp.otp:
#             User.objects.filter(phone=phone).update(is_active=True)
#             phone_otp.used = True
#             phone_otp.save()
#             return Response({"success": True}, status=status.HTTP_200_OK)
#         return Response({"success": False, "detail": "Неверный код"},
#                         status=status.HTTP_400_BAD_REQUEST)
#
#
# validate_otp = ValidateOTPView.as_view()


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
