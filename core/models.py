from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django_countries.fields import CountryField


class User(AbstractUser):
    referral = models.CharField(default=False, max_length=50)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    passkey = models.PositiveIntegerField(default=0)
    country = CountryField(default='NG')
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)


class OneTimePassword(models.Model):
    verification_type = models.CharField(max_length=90)
    code = models.CharField(max_length=5, unique=True)
    created_at = models.DateTimeField(auto_now=True)

    def is_valid(self):
        return timezone.now() < self.created_at + timezone.timedelta(minutes=10)

    def __str__(self):
        return f'{self.verification_type} - {self.code} passcode'
