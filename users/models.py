import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

from payment.models import AuditModel
from utils.validators import phone_regex


class CustomUserManager(BaseUserManager):

    def create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        username = self.normalize_email(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('has_dept', False)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(username, password, **extra_fields)


class User(AbstractUser):
    gender_choices = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        blank=True,
        null=True,
    )
    first_name = models.CharField(max_length=100, null=True, blank=False)
    last_name = models.CharField(max_length=100, null=True, blank=False)
    phone = models.CharField(validators=[phone_regex], max_length=20, blank=True)
    profile = models.ImageField(upload_to="profile_picture", blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    reset_otp = models.BooleanField(default=False)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    max_otp_try = models.CharField(max_length=2, default=3)
    otp_max_out = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    has_dept = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False, help_text="Designates whether the broker is locked/deactivated.")

    REQUIRED_FIELDS = ['email']
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username}"

    class Meta:
        db_table = 'users'


class Ads(AuditModel):
    title = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='ads/')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'ads'
        ordering = ['-created_at']
