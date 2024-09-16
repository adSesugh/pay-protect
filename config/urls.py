from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns += [
    re_path(r'^api/', include('djoser.urls')),
    re_path(r'^api/auth/', include('djoser.social.urls')),
    re_path(r'^api/', include('core.urls'), name='core'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)