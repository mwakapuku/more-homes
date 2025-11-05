from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView, SpectacularJSONAPIView, \
    SpectacularRedocView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from mhp import settings
from users.views import CustomLoginView, OTPVerificationView, RequestNewOTPView, ResetPasswordApiView, \
    RequestResetOtpApiView, ChangeUserPasswordApiView, RegisterUserAPIView

schema_view = get_schema_view(
    openapi.Info(
        title="More Homes Project",
        default_version='v1',
        description="API description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="developer@mhp.co.tz"),
        license=openapi.License(name="License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('homes/', include("homes.urls")),
    path('payment/', include("payment.urls")),
    path('auth/', include("users.urls")),
    path('dj-auth/', include('dj_rest_auth.urls')),
    path('api-doc/', SpectacularSwaggerView.as_view(url_name='yaml-schema'), name='swagger-schema'),
    path('schema/yaml-schema/', SpectacularAPIView.as_view(), name='yaml-schema'),
    path('schema/json-schema/', SpectacularJSONAPIView.as_view(), name='json-schema'),
    path('schema/swagger-schema/', SpectacularSwaggerView.as_view(url_name='yaml-schema'), name='swagger-schema'),
    path('schema/redoc-schema/', SpectacularRedocView.as_view(url_name='yaml-schema'), name='redoc-schema'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
