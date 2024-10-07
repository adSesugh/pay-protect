from django.urls import re_path, path
from rest_framework import routers

from core.views import CountryListView, BankViewSet, PayoutAccountViewSet, CustomTokenObtainPairView, ProductViewSet, \
    ContractViewSet, DisputeViewSet, ProtectionFeeViewSet, FAQsViewSet, CustomTokenVerifyView, CustomTokenRefreshView

router = routers.DefaultRouter()
router.register(r'banks', BankViewSet, basename='banks')
router.register(r'payout_accounts', PayoutAccountViewSet, basename='payout')
router.register(r'products', ProductViewSet, basename='products')
router.register(r'questions', ContractViewSet, basename='questions')
router.register(r'disputes', DisputeViewSet, basename='disputes')
router.register(r'protection-fees', ProtectionFeeViewSet, basename='protection-fees')
router.register(r'faqs', FAQsViewSet, basename='faqs')

urlpatterns = [
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', CustomTokenVerifyView.as_view(), name='token_verify'),
    re_path('countries/', CountryListView.as_view(), name='country_list'),
]

urlpatterns += router.urls
