from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django_countries import countries
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from core.models import Bank, PayoutAccount, Product, ContractQuestion, Dispute, DisputeReason, ProtectionFee
from core.serializers import (
    CountrySerializer,
    BankSerializer,
    PayoutAccountSerializer, CustomTokenObtainPairSerializer, ProductSerializer, ContractQuestionSerializer,
    DisputeSerializer, DisputeReasonSerializer, ProtectionFeeSerializer, AgreementSerializer, ProductReviewSerializer
)

import logging

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = request.user
        logger.info(f"User: {user}, Authenticated: {user.is_authenticated}")
        if user and user.is_authenticated:
            UserModel = get_user_model()
            UserModel.objects.filter(pk=user.pk).update(last_login=now())
            logger.info(f"Updated last_login for User ID: {user.pk}")
        return response


class CountryListView(APIView):
    serializer_class = CountrySerializer

    def get(self, request):
        try:
            countries_list = [{'value': code, 'label': name} for code, name in countries]
            serializer = CountrySerializer(countries_list, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"success": False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BankViewSet(viewsets.ModelViewSet):
    serializer_class = BankSerializer
    queryset = Bank.objects.all()
    permission_classes = [IsAuthenticated]


class PayoutAccountViewSet(viewsets.ModelViewSet):
    serializer_class = PayoutAccountSerializer
    queryset = PayoutAccount.objects.all()
    http_method_names = ['get', 'post', 'put']


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    http_method_names = ['get', 'post', 'put']
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    #permission_classes = [IsAuthenticated]

    @action(
        methods=['get'],
        detail=True,
        url_path='review',
        url_name='review',
        serializer_class=ProductReviewSerializer
    )
    def review(self, request, pk=None):
        product = Product.objects.get(pk=pk)
        serializer = ProductReviewSerializer(product)
        try:
            return Response(serializer.data)
        except:
            return Response({"success": False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['post'],
        detail=True,
        url_path='review-check',
        url_name='review-check',
        serializer_class=AgreementSerializer
    )
    def review_check(self, request, pk=None):
        data = request.data
        data['receiver'] = self.request.user.pk
        serializer = AgreementSerializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"success": False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ContractViewSet(viewsets.ModelViewSet):
    serializer_class = ContractQuestionSerializer
    queryset = ContractQuestion.objects.all()
    http_method_names = ['get', 'post', 'put']


class DisputeViewSet(viewsets.ModelViewSet):
    serializer_class = DisputeSerializer
    queryset = Dispute.objects.all()
    http_method_names = ['get', 'post', 'put']
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    @action(
        detail=False,
        methods=["GET"],
        url_path='reasons',
        url_name='reasons',
        serializer_class=DisputeReasonSerializer
    )
    def get_reasons(self, request, pk=None):
        reasons = DisputeReason.objects.all()
        serializer = DisputeReasonSerializer(reasons, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["POST"],
        url_path='reason',
        url_name='reason',
        serializer_class=DisputeReasonSerializer
    )
    def create_dispute_reason(self, request, pk=None):
        data = request.data
        serializer = DisputeReasonSerializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"success": False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["PUT"],
        url_path='update-reason/(?P<reason_id>[^/.]+)',
        url_name='update-reason',
        serializer_class=DisputeReasonSerializer
    )
    def update_reason(self, request, pk=None, reason_id=None):
        data = request.data
        reason = DisputeReason.objects.get(pk=reason_id)
        reason.reason = data.get("reason")
        serializer = DisputeReasonSerializer(reason, data=data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProtectionFeeViewSet(viewsets.ModelViewSet):
    serializer_class = ProtectionFeeSerializer
    queryset = ProtectionFee.objects.all()
    http_method_names = ['get', 'post', 'put']