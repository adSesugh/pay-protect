from django.urls import re_path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView, TokenObtainPairView

from core import views
from core.views import CountryListView, SendVerificationCodeView, ResendOTPAPIView, OTPVerificationAPIView

router = routers.DefaultRouter()

urlpatterns = [
    re_path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    re_path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    re_path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    re_path('countries/', CountryListView.as_view(), name='country_list'),
    re_path('verify/email-or-phone/', OTPVerificationAPIView.as_view(), name='email-or-phone'),
    re_path('verify/send-code/', SendVerificationCodeView.as_view(), name='send-code'),
    re_path('verify/resend-code/', ResendOTPAPIView.as_view(), name='resend-code'),
]

urlpatterns += router.urls
