from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.timezone import now
from django_countries.serializer_fields import CountryField
from django_countries.serializers import CountryFieldMixin
from djoser.serializers import UserCreatePasswordRetypeSerializer, UserCreateSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from core.models import User


class CountrySerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class CustomUserSerializer(UserCreateSerializer):
    country = CountryField()

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
        }


class CustomUserCreatePasswordRetypeSerializer(CountryFieldMixin, UserCreatePasswordRetypeSerializer):
    class Meta(UserCreatePasswordRetypeSerializer.Meta):
        fields = [*UserCreatePasswordRetypeSerializer.Meta.fields, 'country', 'passkey', 'referral', 'is_phone_verified', 'is_email_verified']
        model = User
        read_only_fields = ['is_phone_verified', 'is_email_verified']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):

        group, created = Group.objects.get_or_create(name='General')

        user = super().create(validated_data)
        user.groups.add(group)

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        if user:
            UserModel = get_user_model()
            UserModel.objects.filter(pk=user.pk).update(last_login=now())
        return data


class VerificationSerializer(serializers.Serializer):
    verification_type = serializers.CharField(write_only=True, required=True)


class CodeVerificationSerializer(serializers.Serializer):
    verification_type = serializers.CharField(write_only=True, required=True)
    otp_code = serializers.IntegerField(write_only=True, max_value=999999)