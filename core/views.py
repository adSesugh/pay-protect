import re
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.timezone import now
from django_countries import countries
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from core.models import OneTimePassword
from core.serializers import CountrySerializer, CustomTokenObtainPairSerializer, VerificationSerializer, \
    CodeVerificationSerializer
from core.utils import generate_otp, send_code_to_user, send_sms_otp, validate_otp


class CountryListView(APIView):
    serializer_class = CountrySerializer

    def get(self, request):
        try:
            countries_list = [{'value': code, 'label': name} for code, name in countries]
            serializer = CountrySerializer(countries_list, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"success": False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = request.user
        if user and user.is_authenticated:
            UserModel = get_user_model()
            UserModel.objects.filter(pk=user.pk).update(last_login=now())
        return response


class SendVerificationCodeView(APIView):
    serializer_class = VerificationSerializer

    def post(self, request, *args, **kwargs):
        verification_type = request.data.get('verification_type')

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        phone_regex = r'^\+?[1-9]\d{1,14}$'

        if re.match(email_regex, verification_type):
            try:
                send_code_to_user(verification_type)
                return Response({"success": True, 'message': 'OTP sent to email.'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response()

        elif re.match(phone_regex, verification_type):
            try:
                send_sms_otp(verification_type)
                return Response({"success": True, 'message': 'OTP sent to phone.'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response()

        else:
            return Response({"success": False, 'error': 'Invalid contact information. Please enter a valid email or '
                                                        'phone number.'},
                            status=status.HTTP_400_BAD_REQUEST)


class ResendOTPAPIView(APIView):
    serializer_class = VerificationSerializer

    def post(self, request, *args, **kwargs):
        verification_type = request.data.get('verification_type')
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        phone_regex = r'^\+?[1-9]\d{1,14}$'

        # Check if there's an existing OTP that hasn't expired
        existing_otp = OneTimePassword.objects.filter(verification_type=verification_type).order_by('-created_at').first()

        if existing_otp and existing_otp.created_at + timedelta(minutes=5) > timezone.now():
            return Response({"success": False, 'error': 'Cannot resend OTP, try again later.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # If there's an existing OTP, delete it
        if existing_otp:
            existing_otp.delete()

        if re.match(email_regex, verification_type):
            try:
                send_code_to_user(verification_type)
                return Response({"success": True, 'message': 'OTP sent to email.'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response()

        elif re.match(phone_regex, verification_type):
            try:
                send_sms_otp(verification_type)
                return Response({"success": True, 'message': 'OTP sent to phone.'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response()

        else:
            return Response({"success": False, 'error': 'Invalid contact information. Please enter a valid email or '
                                                        'phone number.'},
                            status=status.HTTP_400_BAD_REQUEST)


class OTPVerificationAPIView(APIView):
    serializer_class = CodeVerificationSerializer

    def post(self, request, *args, **kwargs):
        verification_type = request.data.get('verification_type')
        otp_code = request.data.get('otp_code')

        if validate_otp(verification_type, otp_code):
            OneTimePassword.objects.filter(code=otp_code).delete()
            return Response({'success': True, 'message': 'Email verified successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)
