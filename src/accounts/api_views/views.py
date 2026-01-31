import secrets

import requests
from django.conf import settings
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
from django_filters.rest_framework import DjangoFilterBackend

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
                                                UpdateGooglePasswordUserSerializer,
                                                StaffTokenObtainPairSerializer,
                                                UserChangePasswordSerializer,
                                                AllStudentSerializer,
                                                BalanceHistorySerializer,
                                                UserBaseSerializer, CreateLoginTokenSerializer, TelegramSerializer,
                                                BalanceHistoryFileSerializer)
from src.accounts.filters import UserStudentFilter
from src.accounts.models import Role, TelegramToken, BalanceHistory
from src.common.exception import (UnexpectedError, PhoneExistError,
                                  EmailExistError, IsNotStudentError,
                                  IsNotStaffError, UserNotExistError)
from src.common.paginations import SimplePagination
from src.services.permissions import SuperAdminPermission

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
    serializer_class = StaffTokenObtainPairSerializer

    @swagger_auto_schema(tags=["super_admin"])
    def post(self, request, *args, **kwargs):
        # email = self.request.data.get("email")
        # user = User.objects.filter(email=email).first()
        # if user.role.name_code == "student":
        #     raise IsNotStaffError()
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


class AdminUpdateUserPasswordView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated, SuperAdminPermission)
    queryset = User.objects.all()
    serializer_class = UserChangePasswordSerializer
    lookup_field = None
    http_method_names = ['put']

    def update(self, request, *args, **kwargs):
        user_id = self.request.data.get('user_id')
        password = self.request.data.get('password')
        try:
            user = self.queryset.get(user_id=user_id)
            user.set_password(password)
            user.save()
            return Response(
                {"status": True, "detail": "Пароль ауыстырылды"},
                status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"status": False, "detail": "что-то пошло не так"},
                status=status.HTTP_400_BAD_REQUEST)


admin_update_password_view = AdminUpdateUserPasswordView.as_view()


class UserListView(generics.ListAPIView):
    # permission_classes = [permissions.IsAuthenticated, SuperAdminPermission]
    queryset = User.objects.all()
    serializer_class = AllStudentSerializer
    pagination_class = SimplePagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserStudentFilter


user_list_view = UserListView.as_view()


class TeacherListView(generics.ListAPIView):
    # permission_classes = [permissions.IsAuthenticated, SuperAdminPermission]
    queryset = User.objects.filter(role__name_code='teacher')
    serializer_class = UserBaseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserStudentFilter

    def get_queryset(self):
        return super().get_queryset()[:100]


teacher_list_view = TeacherListView.as_view()


class BalanceHistoryView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated, SuperAdminPermission)
    serializer_class = BalanceHistorySerializer

    def perform_create(self, serializer):
        user_id = self.request.data.get("user_id")
        student = User.objects.filter(user_id=user_id).first()
        serializer.save(
            user=self.request.user,
            student=student
        )


add_balance_history = BalanceHistoryView.as_view()

DEFAULT_BALANCE_ADMIN_EMAIL = "yerke@gmail.com"


class BalanceFromExcelView(generics.CreateAPIView):
    """
    Accepts an Excel file with columns LOGIN (email) and AMOUNT.
    For each row: find student by email; if balance < amount, create BalanceHistory
    with balance=(amount - current_balance). Admin user for history: yerke@gmail.com.
    """
    # permission_classes = (permissions.IsAuthenticated, SuperAdminPermission)
    serializer_class = BalanceHistoryFileSerializer

    def post(self, request, *args, **kwargs):
        import openpyxl

        amount_val = request.data.get("amount")
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"detail": "No file provided. Use form field 'file' with an Excel (.xlsx) file."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not file.name.endswith((".xlsx", ".xls")):
            return Response(
                {"detail": "File must be Excel (.xlsx or .xls)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        default_user = User.objects.filter(email=DEFAULT_BALANCE_ADMIN_EMAIL).first()
        if not default_user:
            return Response(
                {"detail": f"Default admin user not found: {DEFAULT_BALANCE_ADMIN_EMAIL}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            wb = openpyxl.load_workbook(file, read_only=True, data_only=True)
            ws = wb.active
            rows = list(ws.iter_rows(values_only=True))
        except Exception as e:
            return Response(
                {"detail": f"Invalid Excel file: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not rows:
            return Response(
                {"detail": "Excel file is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        header = [str(c).strip().upper() if c is not None else "" for c in rows[0]]
        login_col = None
        # amount_col = None
        password_col = None
        for i, h in enumerate(header):
            if h in ("LOGIN", "EMAIL"):
                login_col = i
            if h in ("PASSWORD", "PASSWORD"):
                password_col = i
        if login_col is None:
            return Response(
                {"detail": "Excel must have a column 'LOGIN' or 'EMAIL'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # if amount_col is None:
        #     return Response(
        #         {"detail": "Excel must have a column 'AMOUNT' or 'BALANCE'."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        created = 0
        skipped = 0
        errors = []

        for row_idx, row in enumerate(rows[1:], start=2):
            try:
                email_val = row[login_col] if login_col < len(row) else None
                password = row[password_col] if password_col < len(row) else None
                # amount_val = row[amount_col] if amount_col < len(row) else None
                if email_val is None or (isinstance(email_val, str) and not email_val.strip()):
                    skipped += 1
                    continue
                email = str(email_val).strip().lower()
                if amount_val is None or (isinstance(amount_val, str) and not str(amount_val).strip()):
                    errors.append({"row": row_idx, "email": email, "error": "Amount is empty"})
                    continue
                try:
                    amount = int(float(amount_val))
                except (TypeError, ValueError):
                    errors.append({"row": row_idx, "email": email, "error": "Invalid amount"})
                    continue
                if amount <= 0:
                    errors.append({"row": row_idx, "email": email, "error": "Amount must be positive"})
                    continue

                student = User.objects.filter(
                    email=email,
                    role__name_code="student",
                ).first()
                if not student:
                    errors.append({"row": row_idx, "email": email, "error": "Student not found"})
                    continue
                if student.balance >= amount:
                    skipped += 1
                    continue
                add_balance = amount - student.balance
                student.set_password(password)
                BalanceHistory.objects.create(
                    student=student,
                    user=default_user,
                    balance=add_balance,
                    data=f"Excel upload row {row_idx}",
                )
                created += 1
            except Exception as e:
                email_display = str(row[login_col]).strip() if login_col < len(row) and row[
                    login_col] is not None else ""
                errors.append({
                    "row": row_idx,
                    "email": email_display,
                    "error": str(e),
                })

        wb.close()
        return Response(
            {
                "created": created,
                "skipped": skipped,
                "errors": errors,
            },
            status=status.HTTP_200_OK,
        )


add_balance_from_excel = BalanceFromExcelView.as_view()


class CreateLoginTokenAPIView(APIView):
    """API для создания login токена (для бота)"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        print('======')
        auth_header = request.headers.get('Authorization')
        # if auth_header != f"Bearer {settings.TELEGRAM_BOT_TOKEN}":
        #     return Response(
        #         {"detail": "error"},
        #         status=status.HTTP_401_UNAUTHORIZED
        #     )

        serializer = CreateLoginTokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        user, _ = User.objects.get_or_create(
            username=serializer.validated_data.get('username') + '_telegram',

        )
        print(serializer.validated_data.get('first_name'))
        # first_name = serializer.validated_data.get('first_name'),
        # last_name = serializer.validated_data.get('last_name'),
        # telegram_id = serializer.validated_data.get('telegram_id'),
        # is_active = False
        # if user:
        #     user.first_name = serializer.validated_data.get('first_name')
        #     user.last_name = serializer.validated_data.get('first_name')
        #     user.telegram_id = serializer.validated_data.get('first_name')
        token = secrets.token_urlsafe(36)
        TelegramToken.objects.create(
            user=user,
            telegram_user_id=str(serializer.validated_data.get('telegram_id')),
            token=token,
            used=False
        )
        return Response(
            {
                "token": token
            },
            status=status.HTTP_200_OK
        )


create_login_token_api_view = CreateLoginTokenAPIView.as_view()


class TelegramJWTView(APIView):
    @swagger_auto_schema(request_body=TelegramSerializer)
    def post(self, request, *args, **kwargs):
        token = request.data.get('token', None)
        if not token:
            return None
        telegram_token = TelegramToken.objects.filter(token=token).first()
        telegram_token.used = True
        telegram_token.save()
        user = telegram_token.user
        user.is_active = True
        user.save()

        refresh = TokenObtainPairSerializer.get_token(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return Response(data, status=status.HTTP_200_OK)


telegram_view = TelegramJWTView.as_view()


def telegram_auth_page_view(request):
    """
    Страница с кнопкой для открытия Telegram бота
    """
    from django.shortcuts import render
    return render(request, 'accounts/telegram_auth_page.html')
