from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from src.accounts.models import Role, TokenVersion

User = get_user_model()


class AuthMeSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='role.name', default=None)

    class Meta:
        model = User
        fields = (
            'id',
            'uuid',
            'role',
            'first_name',
            'last_name',
            'balance',
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
