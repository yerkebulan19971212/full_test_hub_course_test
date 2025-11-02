from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from src.common import abstract_models
from src.common.constant import TestLang


class Role(
    abstract_models.UUID,
    abstract_models.AbstractBaseName,
    abstract_models.AbstractBaseNameCode,
    abstract_models.IsActive,
    abstract_models.Ordering,
    abstract_models.TimeStampedModel
):
    pass

    class Meta:
        db_table = 'accounts\".\"role'

    def __str__(self):
        return self.name_code


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password,
                     **extra_fields):
        """
        Create and save a User with given email, and password.
        """
        if not email:
            raise ValueError('The given username must be set')
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(
    AbstractUser,
    abstract_models.UUID,
    abstract_models.Ordering,
    abstract_models.TimeStampedModel
):
    avatar = models.FileField(
        upload_to="accounts/icon",
        blank=True,
        null=True,
        # validators=[validate_size_image, validate_mb_image]
    )
    username = models.CharField(
        max_length=128,
        unique=True,
        null=True
    )
    email = models.EmailField(
        unique=True,
        null=True,
        db_index=True,
        blank=True
    )
    phone = models.CharField(
        max_length=11,
        unique=True,
        blank=True,
        null=True,
        db_index=True
    )
    role = models.ForeignKey(
        Role,
        related_name='users',
        on_delete=models.CASCADE,
        null=True,
        db_index=True
    )
    language = models.CharField(
        max_length=64,
        choices=TestLang.choices(),
        default=TestLang.KAZAKH,
        db_index=True
    )
    city = models.ForeignKey(
        'common.City',
        on_delete=models.CASCADE,
        null=True,
        db_index=True,
        blank=True
    )
    school = models.ForeignKey(
        'common.School',
        on_delete=models.CASCADE,
        null=True,
        db_index=True,
        blank=True
    )
    balance = models.IntegerField(
        default=0
    )
    birthday = models.DateTimeField(
        null=True,
        blank=True
    )
    is_google = models.BooleanField(default=False)
    user_id = models.IntegerField(
        null=True,
        unique=True,
        blank=True
    )
    login_count = models.IntegerField(default=0)
    telegram_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.username)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.email:
            self.email = self.email.lower()
        if self.username:
            self.username = self.username.lower()
        return super().save()

    def get_full_name(self):
        return " ".join([self.first_name, self.last_name])

    def get_full_name_with_underscore(self):
        return "_".join([self.first_name, self.last_name])

    class Meta:
        db_table = 'accounts\".\"user'


class TokenVersion(abstract_models.UUID, abstract_models.TimeStampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='token_version'
    )
    version = models.IntegerField(default=0)


class TokenHistory(abstract_models.UUID, abstract_models.TimeStampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='token_histories'
    )
    token = models.CharField(max_length=255)


class BalanceHistory(abstract_models.UUID, abstract_models.TimeStampedModel):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='student_balance_histories',
        null=True, blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='admin_balance_histories',
        null=True, blank=True
    )
    balance = models.IntegerField()
    data = models.TextField(null=True, blank=True)


class TelegramToken(
    abstract_models.UUID,
    abstract_models.TimeStampedModel
):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='telegram_users',
        null=True, blank=True
    )
    telegram_user_id = models.IntegerField(default=0)
    token = models.CharField(max_length=255)
    used = models.BooleanField(default=False)
