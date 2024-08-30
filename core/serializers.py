from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.timezone import now
from django_countries.serializer_fields import CountryField
from djoser.serializers import UserCreatePasswordRetypeSerializer, UserCreateSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.models import User, Bank, PayoutAccount


class CountrySerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class CustomUserSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
        }


class CustomUserCreatePasswordRetypeSerializer(UserCreatePasswordRetypeSerializer):
    class Meta(UserCreatePasswordRetypeSerializer.Meta):
        fields = [*UserCreatePasswordRetypeSerializer.Meta.fields]
        model = User
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        group, created = Group.objects.get_or_create(name='Seller')

        user = super().create(validated_data)
        user.groups.add(group)

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims here if needed
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        if user:
            UserModel = get_user_model()
            UserModel.objects.filter(pk=user.pk).update(last_login=now())
        return data


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

    def create(self, validated_data):
        user = self.context['request'].user
        bank = Bank.objects.create(**validated_data, user=user if user else None)
        return bank


class PayoutAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayoutAccount
        fields = '__all__'
        read_only_fields = ['id']
        db_table = 'payout_accounts'

    def create(self, validated_data):
        payout_account = PayoutAccount.objects.create(**validated_data)
        return payout_account
