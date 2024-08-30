from django.urls import re_path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from core import views
from core.views import CountryListView, BankViewSet, PayoutAccountViewSet, CustomTokenObtainPairView

router = routers.DefaultRouter()
router.register(r'banks', BankViewSet, basename='banks')
router.register(r'payout_accounts', PayoutAccountViewSet, basename='payout_accounts')

urlpatterns = [
    re_path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    re_path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    re_path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    re_path('countries/', CountryListView.as_view(), name='country_list'),
]

urlpatterns += router.urls
