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
                                                RegisterEmailSerializer,
                                                OwnRefreshToken,
                                                TokenObtainPairSerializerByEmail,
                                                TokenObtainPairSerializerByPhone,
                                                UpdatePasswordSerializer,
                                                UpdateUserSerializer,
                                                ProfileUserSerializer,
                                                UpdateLoginProfileUserSerializer,
                                                UpdateGooglePasswordUserSerializer)
from src.accounts.models import Role
from src.common.exception import (UnexpectedError, PhoneExistError,
                                  EmailExistError, IsNotStudentError,
                                  IsNotStaffError, UserNotExistError)

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
        res = self.create(request, *args, **kwargs)
        if res.status_code == status.HTTP_201_CREATED:
            user = User.objects.filter(phone=phone).first()
            token = OwnRefreshToken.for_user(user)
            return Response(
                {"refresh": str(token), "access": str(token.access_token)})
        return res


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
        res = self.create(request, *args, **kwargs)
        if res.status_code == status.HTTP_201_CREATED:
            user = User.objects.filter(email=email).first()
            token = OwnRefreshToken.for_user(user)
            return Response(
                {"refresh": str(token), "access": str(token.access_token)})
        return res


register_email_view = RegisterStudentEmailUserView.as_view()


class TokenObtainPairByPhoneView(BaseTokenObtainPairView):
    serializer_class = TokenObtainPairSerializerByPhone

    def post(self, request, *args, **kwargs):
        phone = self.request.data.get("phone")
        user = User.objects.filter(phone=phone).first()
        if user is None:
            raise UserNotExistError()
        if user.role.name_code != "student":
            raise IsNotStudentError()
        return super().post(request, *args, **kwargs)


token_by_phone_view = TokenObtainPairByPhoneView.as_view()


class TokenObtainPairByEmailView(BaseTokenObtainPairView):
    serializer_class = TokenObtainPairSerializerByEmail

    def post(self, request, *args, **kwargs):
        email = self.request.data.get("email")
        user = User.objects.filter(email=email).first()
        if user is None:
            raise UserNotExistError()
        if user.role.name_code != "student":
            raise IsNotStudentError()
        return super().post(request, *args, **kwargs)


token_by_email_view = TokenObtainPairByEmailView.as_view()


class StaffTokenObtainPairView(BaseTokenObtainPairView):
    """ логин для сотрудников """
    serializer_class = TokenObtainPairSerializerByEmail

    def post(self, request, *args, **kwargs):
        email = self.request.data.get("email")
        user = User.objects.filter(email=email).first()
        if user.role.name_code == "student":
            raise IsNotStaffError()
        return super().post(request, *args, **kwargs)


token_staff_view = StaffTokenObtainPairView.as_view()


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
            user.is_google = True
            user.role = Role.objects.filter(name_code='student').first()
            user.password = 'google'
            user.save()
        refresh = TokenObtainPairSerializer.get_token(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return Response(data, status=status.HTTP_200_OK)


google = GoogleJWTView.as_view()


class UpdatePasswordView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdatePasswordSerializer
    http_method_names = ['put']
    lookup_field = None

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        res = self.update(request, *args, **kwargs)
        if res.status_code == status.HTTP_200_OK:
            user = self.get_object()
            token = OwnRefreshToken.for_user(user)
            return Response(
                {"refresh": str(token), "access": str(token.access_token)})


update_password_view = UpdatePasswordView.as_view()


class UpdateProfileView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdateUserSerializer
    http_method_names = ['patch']
    lookup_field = None

    def get_object(self):
        return self.request.user


update_profile_view = UpdateProfileView.as_view()


class ProfileUserView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileUserSerializer
    lookup_field = None

    def get_object(self):
        return self.request.user


profile_view = ProfileUserView.as_view()


class UpdateLoginProfileView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdateLoginProfileUserSerializer
    http_method_names = ['patch']
    lookup_field = None

    def get_object(self):
        return self.request.user


update_login_profile_view = UpdateLoginProfileView.as_view()


class UpdateGooglePasswordView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdateGooglePasswordUserSerializer
    http_method_names = ['patch']
    lookup_field = None

    def get_object(self):
        return self.request.user


update_google_password_view = UpdateGooglePasswordView.as_view()
