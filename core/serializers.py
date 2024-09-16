from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from djoser.serializers import UserCreatePasswordRetypeSerializer, UserCreateSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.models import User, Bank, PayoutAccount, Product, ProductImage, ContractQuestion, DisputeReason, Dispute, \
    ProtectionFee, Agreement, DisputeImage


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

    # def create(self, validated_data):
    #     group, created = Group.objects.get_or_create(name='Seller')
    #
    #     user = super().create(validated_data)
    #     user.groups.add(group)
    #
    #     return user


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


class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',]


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


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProductImage
        fields = ['id', 'image']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else settings.DEFAULT_HOST + obj.image.url
        return None


class ProductSerializer(serializers.ModelSerializer):
    photo = serializers.ListField(
        child=serializers.ImageField(),
        required=True,
        write_only=True
    )
    images = serializers.SerializerMethodField(read_only=True)
    user = UserDataSerializer(read_only=True)
    receiver = UserDataSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'amount', 'fee', 'photo', 'images', 'user', 'receiver']
        read_only_fields = ['id', 'user', 'receiver']

    def get_images(self, obj):
        photos = ProductImage.objects.filter(product=obj)
        serializer = ProductImageSerializer(photos, many=True)
        return serializer.data

    def create(self, validated_data):
        # current user who also may serve as initiator
        user = self.context['request'].user

        # Extract the photo data from the validated data
        photos = validated_data.pop('photo')

        # Create the product instance
        product = Product.objects.create(**validated_data, user=user)

        # Iterate over the photo data and create ProductImage instances
        for photo in photos:
            ProductImage.objects.create(product=product, image=photo)

        return product


class ContractQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractQuestion
        fields = ['id', 'question', 'additions']
        read_only_fields = ['id']


class DisputeReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisputeReason
        fields = '__all__'
        read_only_fields = ('user',)


class DisputeSerializer(serializers.ModelSerializer):
    image = serializers.ListField(
        child=serializers.ImageField(),
        required=True,
        write_only=True
    )
    dispute_photos = serializers.SerializerMethodField(read_only=True)
    product = serializers.SerializerMethodField(read_only=True)
    user = UserDataSerializer(read_only=True)

    class Meta:
        model = Dispute
        fields = ['id', 'user', 'product', 'reason', 'description', 'image', 'user', 'dispute_photos']
        depth = 1

    def get_dispute_photos(self, obj):
        photos = DisputeImage.objects.filter(dispute=obj)
        serializer = DisputeImageSerializer(photos, many=True)
        return serializer.data

    def get_product(self, obj):
        product = Product.objects.filter(id=obj.product.id).first()
        serializer = ProductSerializer(product)
        return serializer.data

    def create(self, validated_data):
        # current user who also may serve as initiator
        user = self.context['request'].user

        # Extract the photo data from the validated data
        photos = validated_data.pop('image')

        # Create the product instance
        dispute = Dispute.objects.create(**validated_data, user=user)

        # Iterate over the photo data and create ProductImage instances
        for photo in photos:
            DisputeImage.objects.create(dispute=dispute, photo=photo)

        return dispute


class AgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agreement
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at',)


class ProtectionFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProtectionFee
        fields = '__all__'
        read_only_fields = ('user', 'id', 'created_at', 'updated_at',)

    def create(self, validated_data):
        user = self.context['request'].user
        return ProtectionFee.objects.create(**validated_data, user=user)


class ProductReviewSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField(read_only=True)
    photos = serializers.SerializerMethodField(read_only=True)
    agreement = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'amount', 'fee', 'questions', 'photos', 'agreement']
        read_only_fields = ('id', 'user', 'created_at', 'updated_at',)
        depth = 1

    def get_photos(self, obj):
        photo = ProductImage.objects.filter(product=obj)
        return ProductImageSerializer(photo, many=True).data

    def get_questions(self, obj):
        questions = ContractQuestion.objects.all()
        serializer = ContractQuestionSerializer(questions, many=True)
        return serializer.data

    def get_agreement(self, obj):
        agreement = Agreement.objects.filter(product=obj)
        serializer = AgreementSerializer(agreement, many=True)
        return serializer.data


class DisputeImageSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DisputeImage
        fields = '__all__'

    def get_photo(self, obj):
        request = self.context.get('request')
        if obj.photo:
            return request.build_absolute_uri(obj.photo.url) if request else settings.DEFAULT_HOST + obj.photo.url
        return None
