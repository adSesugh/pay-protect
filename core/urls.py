from django.urls import re_path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from core import views
from core.views import CountryListView, BankViewSet, PayoutAccountViewSet, CustomTokenObtainPairView, ProductViewSet, \
    ContractViewSet, DisputeViewSet, ProtectionFeeViewSet

router = routers.DefaultRouter()
router.register(r'banks', BankViewSet, basename='banks')
router.register(r'payout_accounts', PayoutAccountViewSet, basename='payout')
router.register(r'products', ProductViewSet, basename='products')
router.register(r'questions', ContractViewSet, basename='questions')
router.register(r'disputes', DisputeViewSet, basename='disputes')
router.register(r'protection-fees', ProtectionFeeViewSet, basename='protection-fees')

urlpatterns = [
    re_path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    re_path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    re_path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    re_path('countries/', CountryListView.as_view(), name='country_list'),
]

urlpatterns += router.urls
