from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django_countries import countries
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from core.models import Bank, PayoutAccount
from core.serializers import (
    CountrySerializer,
    BankSerializer,
    PayoutAccountSerializer, CustomTokenObtainPairSerializer
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


class PayoutAccountViewSet(viewsets.ModelViewSet):
    serializer_class = PayoutAccountSerializer
    queryset = PayoutAccount.objects.all()
