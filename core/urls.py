from django.urls import re_path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView, TokenObtainPairView

from core import views

router = routers.DefaultRouter()

urlpatterns = [
    re_path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    re_path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    re_path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

urlpatterns += router.urls
