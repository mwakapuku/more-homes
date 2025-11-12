
from django.urls import path, include
from users.views import CustomLoginView, OTPVerificationView, RequestNewOTPView, ResetPasswordApiView, \
    RequestResetOtpApiView, ChangeUserPasswordApiView, RegisterUserAPIView, GroupApiView


urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='rest_login'),
    path('registration/', RegisterUserAPIView.as_view(), name='rest_register'),
    path('request/reset-token', RequestResetOtpApiView.as_view(), name='request_reset_otp'),
    path('reset/user-password', ResetPasswordApiView.as_view(), name='reset_password_with_otp'),
    path('user-change-password', ChangeUserPasswordApiView.as_view(), name='change_password'),
    path('otp/verify/', OTPVerificationView.as_view(), name='otp_verify'),
    path('otp/request/', RequestNewOTPView.as_view(), name='otp_request'),
    path('roles/', GroupApiView.as_view(), name='groups'),
]

