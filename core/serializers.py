from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer, \
    TokenVerifySerializer
from rest_framework_simplejwt.tokens import UntypedToken, RefreshToken

from core.models import User, Bank, PayoutAccount, Product, ProductImage, ContractQuestion, DisputeReason, Dispute, \
    ProtectionFee, Agreement, DisputeImage, FAQs
from core.utils import generate_random_string, generate_referral_code


class CountrySerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


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


class CustomTokenVerifySerializer(TokenVerifySerializer):
    def validate(self, attrs):
        token = attrs['token']
        try:
            # Check if the token is valid
            UntypedToken(token)
        except (TokenError, InvalidToken) as e:
            raise serializers.ValidationError("Token is invalid or expired")

        # Add custom validation or logic here, if needed
        return attrs


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])
        data = {'access': str(refresh.access_token)}

        # Custom logic here (e.g., logging)

        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'terms',
            'referral_code'
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.referral_code = generate_referral_code(user.id)

        groups, created = Group.objects.get_or_create(name='User')
        user.groups.add(groups)
        user.save()

        return user


class UserNotificationSettingsSerializer(serializers.ModelSerializer):
    notify_on_request = serializers.BooleanField(default=False)
    notify_on_payment = serializers.BooleanField(default=False)
    notify_on_milestone = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = ['notify_on_request', 'notify_on_payment', 'notify_on_milestone']


class UserProfilePhotoSerializer(serializers.ModelSerializer):
    photo_url = serializers.ImageField(required=True)

    class Meta:
        model = User
        fields = ['photo_url']


class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'groups']


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

    def get_image(self, obj) -> str:
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

    def get_images(self, obj) -> list:
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


class DisputeStatusSerializer(serializers.Serializer):
    status = serializers.CharField()


class DisputeSerializer(serializers.ModelSerializer):
    image = serializers.ListField(
        child=serializers.ImageField(),
        required=True,
        write_only=True
    )
    product_id = serializers.IntegerField(write_only=True)
    reason_id = serializers.IntegerField(write_only=True)
    dispute_photos = serializers.SerializerMethodField(read_only=True)
    product = serializers.SerializerMethodField(read_only=True)
    user = UserDataSerializer(read_only=True)

    class Meta:
        model = Dispute
        fields = [
            'id',
            'user',
            'product',
            'reason',
            'description',
            'image',
            'user',
            'dispute_photos',
            'product_id',
            'reason_id',
            'status'
        ]
        depth = 1
        write_only_fields = ['reason_id', 'product_id']

    def get_dispute_photos(self, obj) -> list:
        photos = DisputeImage.objects.filter(dispute=obj)
        serializer = DisputeImageSerializer(photos, many=True)
        return serializer.data

    def get_product(self, obj) -> dict:
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

    def get_photos(self, obj) -> list:
        photo = ProductImage.objects.filter(product=obj)
        return ProductImageSerializer(photo, many=True).data

    def get_questions(self, obj) -> list:
        questions = ContractQuestion.objects.all()
        serializer = ContractQuestionSerializer(questions, many=True)
        return serializer.data

    def get_agreement(self, obj) -> list:
        agreement = Agreement.objects.filter(product=obj)
        serializer = AgreementSerializer(agreement, many=True)
        return serializer.data


class DisputeImageSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DisputeImage
        fields = '__all__'

    def get_photo(self, obj) -> str:
        request = self.context.get('request')
        if obj.photo:
            return request.build_absolute_uri(obj.photo.url) if request else settings.DEFAULT_HOST + obj.photo.url
        return None


class FAQsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQs
        fields = '__all__'
        read_only_fields = ('user',)

    def create(self, validated_data):
        user = self.context['request'].user
        return FAQs.objects.create(**validated_data, user=user)
