import secrets
import string
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max, Count
from rest_framework import status
from rest_framework import generics
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
                                                StudentLessonSerializer,
                                                AddTeacherSerializer,
                                                CuratorSerializer,
                                                CreateStudentSerializer,
                                                GetTeacherSerializer,
                                                UserChangePasswordSerializer,
                                                SendPasswordToEmailSerializer,
                                                ValidateOtpSerializer)

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


class CreateStudentUserView(generics.CreateAPIView):
    serializer_class = CreateStudentSerializer

    def post(self, request, *args, **kwargs):
        phone = self.request.data.get('phone').lower()
        user = User.objects.filter(
            phone=phone, role__name='student')

        if user.filter(is_active=True).exists():
            return Response(
                {'detail': 'Такой пользователь уже существует'},
                status=status.HTTP_400_BAD_REQUEST
            )
        not_active_user = user.filter(is_active=False)
        if not_active_user.exists():
            not_active_user.delete()
        return self.create(request, *args, **kwargs)


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
