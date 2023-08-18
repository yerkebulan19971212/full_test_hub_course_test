from django.contrib.auth import get_user_model
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from django.core.mail import send_mail
import secrets
import string
from rest_framework_simplejwt.serializers import \
    TokenObtainPairSerializer as BaseTokenObtainPairSerializer, \
    TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from src.accounts.models import Role, TokenVersion

# from src.quizzes.api_views.serializers import LessonSerializer, \
#     LessonPairListSerializer
# from config.celery import send_to_mail

User = get_user_model()


class AuthMeSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='role.name')

    class Meta:
        model = User
        fields = (
            'uuid',
            'role',
            'first_name',
            'last_name'
        )


class UserDefaultInformation(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'phone',
        )


# class CityListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = City
#         fields = (
#             'id',
#             'name'
#         )


# class AllUserInformationSerializer(serializers.ModelSerializer):
#     user_generates = serializers.SerializerMethodField()
#     lesson_pair = LessonPairListSerializer()
#     city = CityListSerializer()
#
#     class Meta:
#         model = User
#         fields = (
#             'id',
#             'first_name',
#             'last_name',
#             'phone',
#             'iin',
#             'lesson_pair',
#             'city',
#             'user_generates'
#         )
#
#     def get_user_generates(self, obj):
#         last = [i for i in obj.user_generates.all().order_by('id')]
#         if last:
#             return last[-1].password
#         return ''
#

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


# class TeacherLessonSerializer(serializers.ModelSerializer):
#     # lessons = serializers.SerializerMethodField()
#
#     class Meta:
#         model = User
#         fields = (
#             'id',
#             'first_name',
#             'last_name',
#             # 'email',
#         )
#
#     def get_lessons(self, obj):
#         test_lessons = obj.teacher_lessons.select_related('lesson').all()
#         lessons = [t_l.lesson for t_l in test_lessons]
#         lessons_serializer = LessonSerializer(lessons, many=True)
#         return lessons_serializer.data


class GetTeacherSerializer(serializers.ModelSerializer):
    flows = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'user',
            'flows'
        )

    def get_flows(self, obj):
        flows = [i.flow_id for i in obj.user_flows.all()]
        # flows_serializer = FlowNameSerializer(flows, many=True)

        return flows

    def get_user(self, obj):
        user = UserDefaultInformation(obj)
        return user.data


class CuratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id',
                  'first_name',
                  'last_name',
                  # 'email'
                  )


class StudentLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id',
                  'first_name',
                  'last_name',
                  # 'email'
                  )


def create_user(data, role_name):
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(8))
    data['email'] = data['email'].lower()
    data['username'] = data['email'].lower()
    email = data.get('email')
    role = Role.objects.filter(name=role_name).first()
    user = User.objects.filter(email=email, is_active=True, role=role)
    if user.exists():
        return user.first()
    user = User.objects.create(**data,
                               is_active=True,
                               role=role)
    user.set_password(password)
    user.save()
    # send_to_mail.delay(
    #     [email],
    #     "Ваш пароль: " + password,
    #     'Password'
    # )
    return user


class CreateStudentSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=False, read_only=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'phone',
            'iin',
            'lesson_pair',
            'city',
            'is_active',
            'password'
        )

    def create(self, validated_data):
        validated_data['is_active'] = False
        password = validated_data.pop('password')
        role = Role.objects.filter(name='student').first()
        validated_data['role'] = role
        user = super().create(validated_data=validated_data)
        user.set_password(password)
        user.save()

        return user


class AddTeacherSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=32, default='123')

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            # 'email',
            'phone',
            'password'
        )

    def create(self, validated_data):
        user = create_user(validated_data, 'teacher')

        return user


class AdviserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            # 'email',
            'phone',
        )

    def create(self, validated_data):
        user = create_user(validated_data, 'adviser')

        return user


class GetAdviserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            # 'email',
            'phone',
        )


class GetAdviserWithoutIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            # 'email',
            'phone',
        )


class RetrieveAdviserSerializer(serializers.ModelSerializer):
    teachers = serializers.SerializerMethodField()
    adviser = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'adviser',
            'teachers'
        )

    def get_adviser(self, obj):
        return GetAdviserWithoutIdSerializer(obj).data

    def get_teachers(self, obj):
        teachers = obj.teachers.all()
        return [t.teacher.id for t in teachers]


#
# class StudentResultSerializer(serializers.ModelSerializer):
#     lesson_name = serializers.CharField(source='variant_lesson.lesson.name_ru')
#     lesson_id = serializers.IntegerField(source='variant_lesson.lesson.id')
#     student = UserDefaultInformation()
#
#     class Meta:
#         model = StudentResult
#         fields = (
#             'id',
#             'student',
#             'quantity',
#             'lesson_name',
#             'lesson_id',
#             'file'
#         )
#

# class StudentEntResultSerializer(serializers.ModelSerializer):
#     student = UserDefaultInformation()
#     lesson_pair = LessonPairListSerializer()
#     variant_name = serializers.DateTimeField(
#         source='student_test.variant.name')
#     end_time = serializers.DateTimeField(source='student_test.test_end_time')
#
#     class Meta:
#         model = StudentEntResult
#         fields = (
#             'id',
#             'student',
#             'lesson_pair',
#             'mat_quantity',
#             'student_test',
#             'gramot_quantity',
#             'history_quantity',
#             'prof_1_quantity',
#             'prof_2_quantity',
#             'total',
#             'variant_name',
#             'end_time'
#         )
#

class UserChangePasswordSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField()

    #
    # def update(self, instance, validated_data):
    #     validated_data['phone'] = validated_data.pop('phone').lower()
    #
    #     alphabet = string.ascii_letters + string.digits
    #     password = ''.join(secrets.choice(alphabet) for i in range(8))
    #     instance.set_password(password)
    #     instance.save()
    #
    #     return instance


class SendPasswordToEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'phone',
            'password'
        )


class StudentInformationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            # 'email'
        )


# class PhoneOtpSerializer(serializers.ModelSerializer):
#     phone = serializers.CharField()
#     forgot = serializers.BooleanField(write_only=True, default=False)
#
#     class Meta:
#         model = PhoneOtp
#         fields = (
#             'pk',
#             'phone',
#             'forgot'
#         )
#
#     def create(self, validated_data):
#         phone = validated_data['phone']
#         forgot = validated_data['forgot']
#         phone_opt = PhoneOtp.create_otp_for_phone(phone=phone, forgot=forgot)
#         return phone_opt


class ValidateOtpSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=10, min_length=6)
    otp = serializers.CharField(max_length=6, min_length=6)
