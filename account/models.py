from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator, validators
from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed
from .mails import send_confirmation_code


# Create your manager here

class CustomUserManager(BaseUserManager):
    def _create_user(self, username: str, email: str, password: str, first_name: str, last_name: str, **extra_fields):
        if not username:
            raise ValueError("Username must be set")
        if not email:
            raise ValueError("Email must be set")
        if not password:
            raise ValueError("Password must be set")
        if not first_name:
            raise ValueError("First name must be set")
        if not last_name:
            raise ValueError("Last name must be set")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(self._db)
        return user

    def create_user(self, username: str, email: str, password: str, first_name: str, last_name: str, **extra_fields):
        extra_fields.setdefault('is_active', False)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, first_name, last_name, **extra_fields)

    def create_superuser(self, username: str, email: str, password: str, first_name: str, last_name: str,
                         **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(username, email, password, first_name, last_name, **extra_fields)


class ActiveUserManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class InactiveUserManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=False)


# Create your models here.


class CUser(AbstractBaseUser, PermissionsMixin):
    # validators
    username_validator = UnicodeUsernameValidator()
    email_validator = validators.EmailValidator()
    photo_validator = validators.FileExtensionValidator(allowed_extensions=['png', 'jpeg', 'jpg'])
    # required fields
    username = models.CharField(unique=True, max_length=255, validators=[username_validator])
    email = models.EmailField(unique=True, validators=[email_validator])
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # optional fields
    photo = models.ImageField(upload_to='users/photos/%Y/%m/%d', blank=True, validators=[photo_validator])
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=150, blank=True)
    available_for_hire = models.BooleanField(default=False)
    # urls
    website = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    twitter = models.URLField(blank=True)

    objects = CustomUserManager()
    active_users = ActiveUserManager()
    inactive_users = InactiveUserManager()

    following = models.ManyToManyField('self', 'followers', symmetrical=False, blank=True)
    number_of_following = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return str(self.username)

    def get_full_name(self):
        return f"{self.first_name.capitalize()} {self.last_name.capitalize()}".strip()

    def get_short_name(self):
        return self.first_name


# create your signals here
@receiver(signal=post_save, sender=CUser)
def send_confirm_email(sender, **kwargs):
    created = kwargs.get('created')
    user: CUser = kwargs.get('instance', None)
    if created:
        send_confirmation_code(user)


@receiver(signal=m2m_changed, sender=CUser.following.through)
def follow_user(sender, **kwargs):
    action = kwargs.get('action')
    user = kwargs.get('instance')
    if action == "post_add" or action == 'post_remove':
        user.number_of_following = user.following.count()
        user.save()
