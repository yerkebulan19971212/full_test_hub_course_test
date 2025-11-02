from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers, exceptions
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from src.accounts.models import Role, TokenVersion, BalanceHistory
from src.common.exception import (PasswordNotCorrectError,
                                  EmailAlreadyExistError, PhoneAlreadyExistError,
                                  AccountDoesNotHavePasswordError, PasswordsDoNotMatchError)

User = get_user_model()


class AuthMeSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='role.name_code', default=None)

    class Meta:
        model = User
        fields = (
            'id',
            'user_id',
            'uuid',
            'role',
            'first_name',
            'last_name',
            'balance',
        )


class UserBaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
        )


class OwnRefreshToken(RefreshToken):

    @classmethod
    def for_user(cls, user):
        """
        Adds this token to the outstanding token list.
        """
        token = super().for_user(user)
        user_id = token['user_id']
        token_version, _ = TokenVersion.objects.get_or_create(user_id=user_id)
        token_version.version += 1
        token_version.save()

        token['version'] = token_version.version

        return token


class TokenObtainPairSerializer(TokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        user.login_count += 1
        user.save()
        return OwnRefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data


class TokenObtainPairSerializerByPhone(TokenObtainPairSerializer):
    username_field = 'phone'


class TokenObtainPairSerializerByEmail(TokenObtainPairSerializer):
    username_field = 'email'


class StaffTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'iin'

    def validate(self, attrs):
        authenticate_kwargs = {
            "phone": attrs[self.username_field],
            "password": attrs["password"],
        }
        try:
            authenticate_kwargs["request"] = self.context["request"]
        except KeyError:
            pass
        self.user = authenticate(**authenticate_kwargs)
        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            raise exceptions.AuthenticationFailed(
                self.error_messages["no_active_account"],
                "no_active_account",
            )
        data = {}
        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return data


class RegisterPhoneSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'phone',
            'password'
        )

    def create(self, validated_data):
        try:
            validated_data["phone"] = validated_data["phone"].lower()
            validated_data["is_active"] = True
            validated_data["username"] = validated_data["phone"].lower()
            password = validated_data.pop("password")
            role = Role.objects.filter(name_code="student").first()
            validated_data["role"] = role
            user = super().create(validated_data=validated_data)
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            raise e


class RegisterEmailSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'password'
        )

    def create(self, validated_data):
        try:
            email = validated_data["email"].lower()
            validated_data["email"] = email
            validated_data["username"] = email
            validated_data["is_active"] = True
            password = validated_data.pop("password")
            role = Role.objects.filter(name_code="student").first()
            validated_data["role"] = role
            user = super().create(validated_data=validated_data)
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            raise e


class GoogleSerializer(serializers.Serializer):
    id_token = serializers.CharField(required=True)


class UpdatePasswordSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'id',
            'current_password',
            'password'
        )

    def update(self, instance, validated_data):
        if instance.is_google:
            raise AccountDoesNotHavePasswordError()
        current_password = validated_data.get('current_password')
        password = validated_data.get('password')
        if instance.check_password(current_password):
            instance.set_password(password)
        else:
            raise PasswordNotCorrectError()
        instance.save()
        return instance


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            # 'avatar',
            'first_name',
            'last_name',
            'school',
            'city',
            'birthday',
        )


class ProfileUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            # 'avatar',
            'first_name',
            'last_name',
            'school',
            'city',
            'birthday',
            'phone',
            'email',
            'is_google',
        )


class UpdateLoginProfileUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'phone',
            'email',
            'password'
        )

    def validate_email(self, value):
        if value:
            if User.objects.filter(email=value, is_active=True).exists():
                raise EmailAlreadyExistError()
        return value

    def validate_phone(self, value):
        if value:
            if User.objects.filter(phone=value, is_active=True).exists():
                raise PhoneAlreadyExistError()
        return value

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data.get("password")):
            raise PasswordNotCorrectError()
        instance.email = validated_data.get("email")
        instance.phone = validated_data.get("phone")
        instance.save()
        return instance


class UpdateGooglePasswordUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True)
    password_2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'id',
            'password',
            'password_2'
        )

    def update(self, instance, validated_data):
        password_2 = validated_data.pop("password_2")
        password = validated_data.pop("password")
        if password_2 != password:
            raise PasswordsDoNotMatchError()
        instance.is_google = False
        instance.set_password(password)
        instance.save()
        return instance


class UserChangePasswordSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    password = serializers.CharField()


class AllStudentSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='role.name', default=None)

    class Meta:
        model = User
        fields = (
            'user_id',
            'phone',
            'id',
            'uuid',
            'role',
            'first_name',
            'last_name',
            'balance',
        )


class StudentInformationUpdateSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='role.name', default=None)

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'role',
            'last_name',
            'user_id',
            'phone',
            'balance',
            'city',
            'school'
        )


class StudentDetailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'user_id',
            'phone',
            'balance',
            'city',
            'school'
        )


class BalanceHistorySerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(default=6001)

    class Meta:
        model = BalanceHistory
        fields = (
            'id',
            'user_id',
            'balance'
        )

    def create(self, validated_data):
        user_id = validated_data.pop("user_id")
        user = User.objects.filter(is_superuser=True).first()
        validated_data['user'] = user
        return super().create(validated_data)


class CreateLoginTokenSerializer(serializers.Serializer):
    """Сериализатор для создания login токена (используется ботом)"""
    telegram_id = serializers.IntegerField(required=True)
    username = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=255
    )
    first_name = serializers.CharField(required=True, max_length=255)
    last_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255
    )

    def validate_telegram_id(self, value):
        """Проверка telegram_id"""
        if value <= 0:
            raise serializers.ValidationError("telegram_id должен быть положительным числом")
        return value

    def validate_first_name(self, value):
        """Проверка first_name"""
        if not value or not value.strip():
            raise serializers.ValidationError("first_name не может быть пустым")
        return value.strip()



class TelegramSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)