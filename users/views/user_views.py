import random
from datetime import timedelta

from dj_rest_auth.views import LoginView
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from utils.function import send_sms_to_user
from utils.logger import AppLogger
from utils.otp_util import OtpUtil
from utils.response_utils import create_response, create_auth_response
from utils.validators import validate_phone
from ..actions import change_user_password
from ..selectors import verify_phone, get_user_phone, check_user_by_phone, check_password_match, check_current_password
from ..serializers import UserProfileSerializer, RequestNewOTPSerializer, OTPVerificationSerializer, \
    ResetPasswordSerializer, ChangePasswordSerializer, LoginSerializer

logger = AppLogger(__name__)


# Helper function to generate and send OTP
def generate_and_send_otp(user):
    if not user.phone:
        return False

    otp_code = str(random.randint(1000, 9999))
    user.otp = otp_code
    user.otp_expiry = timezone.now() + timedelta(minutes=2)
    user.max_otp_try = 3
    user.otp_max_out = None
    user.save()

    print(f"DEBUG: Sending OTP {otp_code} to {user.phone} for user {user.username}")
    send_sms_to_user(user.phone, f"Your OTP is: {otp_code}")
    return True


class CustomLoginView(LoginView):

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: {"msg": "Login successful and JWT tokens returned."},
            202: {"detail": "OTP sent to your phone for verification.", "otp_required": True},
            401: "Unauthorized - invalid credentials or OTP sending failed",
            400: "Bad request - invalid input data",
        },
        tags=["auth"],
        summary="User login with OTP handling",
        description="Authenticates a user. If the account is verified, returns JWT tokens; otherwise, sends an OTP for verification.",
    )
    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)

        self.user = self.serializer.validated_data['user']

        # Bypass OTP verification for active user
        if self.user.verified:
            refresh = RefreshToken.for_user(self.user)
            user_serializer = UserProfileSerializer(instance=self.user)
            msg = "Login successfully."
            access_token = refresh.access_token
            return create_auth_response(msg, access_token, refresh, user_serializer.data, status.HTTP_200_OK)

        if not self.user.verified:
            otp_util = OtpUtil(self.user)
            otp_is_sent, msg = otp_util.generate_and_send_otp()
            if otp_is_sent:
                msg = "OTP sent to your phone for verification."
                body = {
                    "detail": msg,
                    "phone": self.user.phone,
                    "otp_required": True
                }
                return Response(body, status=status.HTTP_202_ACCEPTED)
            else:
                msg = f"Account not verified, but could not send OTP ({msg}). Please contact support."
                return create_response(msg, status.HTTP_401_UNAUTHORIZED)

        return super().post(request, *args, **kwargs)


class RegisterUserAPIView(APIView):
    @extend_schema(
        request=UserProfileSerializer,
        responses={
            201: {"msg": "Account created successfully"},
            400: "Bad request"
        },
        tags=["auth"],
        summary="Register a new user",
        description="Creates a new user account with provided details like name, email, phone, username, and password."
    )
    def post(self, request):
        serializer = UserProfileSerializer(data=request.data)
        password = request.data.get('password')
        username = request.data.get('username', None)
        phone = request.data.get('phone', None)

        if username is None:
            msg = f"Username is required."
            return create_response(msg, status.HTTP_409_CONFLICT)

        if not validate_phone(phone):
            msg = f"Invalid phone number."
            return create_response(msg, status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            msg = f"User {username} with the same username already exists."
            return create_response(msg, status.HTTP_409_CONFLICT)

        if User.objects.filter(email=request.data['email']).exists():
            msg = f"User {username} with the same email already exists."
            return create_response(msg, status.HTTP_409_CONFLICT)

        if User.objects.filter(phone=phone).exists():
            msg = f"User {username} with the same phone already exists."
            return create_response(msg, status.HTTP_409_CONFLICT)

        if serializer.is_valid():
            serializer.save()
            get_user = User.objects.filter(username=username).first()
            get_user.set_password(password)
            get_user.save()
            msg = "Account created successfully, please login"
            return create_response(msg, status.HTTP_201_CREATED)

        msg = f"{serializer.errors}, try again later"
        return create_response(msg, status.HTTP_400_BAD_REQUEST)


class OTPVerificationView(APIView):
    @extend_schema(
        request=OTPVerificationSerializer,
        responses={
            200: {"msg": "OTP verified successfully and user authenticated."},
            400: "Bad request - invalid OTP, expired OTP, or user not found",
        },
        tags=["auth"],
        summary="Verify OTP and authenticate user",
        description="Verifies the OTP sent to the user's phone and issues JWT tokens upon successful verification.",
    )
    def post(self, request, *args, **kwargs):
        serializer = OTPVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        otp_code = serializer.validated_data['otp']

        if not verify_phone(phone):
            msg = "Multiple accounts found. Please contact support. or account does not exist"
            return create_response(msg, status.HTTP_400_BAD_REQUEST)

        if get_user_phone(phone) is None:
            msg = "No user found with the given phone number"
            return create_response(msg, status.HTTP_400_BAD_REQUEST)

        user = get_user_phone(phone)
        otp_util = OtpUtil(user)

        if not otp_util.verify_otp_max_time():
            msg = "Too many OTP attempts. Try again later. (after 10 minutes)"
            return create_response(msg, status.HTTP_400_BAD_REQUEST)

        if not otp_util.verify_otp_expiry():
            return create_response("OTP expired", status.HTTP_400_BAD_REQUEST)

        if otp_util.check_max_limit():
            msg = "Incorrect OTP. Too many attempts. Please try again after 5 minutes."
            return create_response(msg, status.HTTP_400_BAD_REQUEST)

        if not otp_util.verify_otp(otp_code):
            msg = "Invalid otp"
            msg = otp_util.decrease_max_retries()
            return create_response(f"{msg}", status.HTTP_400_BAD_REQUEST)

        # Verify OTP
        # --- JWT TOKEN GENERATION AND RETURN ---
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        refresh_token = refresh

        user_serializer = UserProfileSerializer(user, context={'request': request})
        user_data = user_serializer.data

        # verify user
        if otp_util.verify_user():
            msg = "OTP verified successfully. and user account verified successfully"
        else:
            msg = "OTP verified successfully. but user account not successfully verified"
        return create_auth_response(msg, access_token, refresh_token, user_data, status.HTTP_200_OK)


class RequestNewOTPView(APIView):

    @extend_schema(
        request=RequestNewOTPSerializer,
        responses={
            200: {"detail": "New OTP sent successfully."},
            404: {"detail": "User not found."},
            400: "Bad request - invalid phone number or data",
        },
        tags=["auth"],
        summary="Request a new OTP code",
        description="Generates and sends a new OTP to the user's registered phone number.",
    )
    def post(self, request, *args, **kwargs):
        serializer = RequestNewOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Generate new OTP
        otp_code = str(random.randint(100000, 999999))
        user.otp = otp_code
        user.otp_expiry = timezone.now() + timedelta(minutes=2)
        user.save()

        generate_and_send_otp(user)
        print(f"Sending OTP {otp_code} to {user.phone}")

        return Response({"detail": "New OTP sent successfully."}, status=status.HTTP_200_OK)


class RequestResetOtpApiView(APIView):
    @extend_schema(
        request=None,
        responses={
            200: {"msg": "OTP sent to your phone for verification."},
            400: "Bad request - invalid or multiple phone accounts",
        },
        tags=["auth"],
        summary="Request OTP for password reset",
        description="Sends an OTP to the user's registered phone number for password reset verification.",
    )
    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        if not check_user_by_phone(phone):
            msg = "No user found with given phone number"
            return create_response(msg, response_status=status.HTTP_400_BAD_REQUEST)
        if not verify_phone(phone):
            msg = "The phone number have more than one account, contact system admin"
            return create_response(msg, response_status=status.HTTP_400_BAD_REQUEST)

        user = get_user_phone(phone)
        otp_util = OtpUtil(user, reset_otp=True)

        if otp_util.generate_and_send_otp():
            msg = "OTP sent to your phone for verification."
            data = UserProfileSerializer(user, context={'request': request}).data
            return create_response(msg, response_status=status.HTTP_200_OK, total_item=1, data=data)
        else:
            msg = "Fail to request token Please contact support."
            return create_response(msg, response_status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordApiView(APIView):

    @extend_schema(
        request=ResetPasswordSerializer,
        responses={
            200: {"msg": "Password reset successfully"},
            400: "Bad request - invalid data, incorrect OTP, or password mismatch",
            500: "Internal server error",
        },
        tags=["auth"],
        summary="Reset password with OTP verification",
        description="Allows a user to reset their password using phone number and OTP verification.",
    )
    def post(self, request, *args, **kwargs):
        try:
            serializer = ResetPasswordSerializer(data=request.data)
            if serializer.is_valid():
                phone = request.data.get('phone')
                otp_code = request.data.get('otp')
                password = request.data.get('confirm_password')
                confirm_password = request.data.get('confirm_password')

                if not check_user_by_phone(phone):
                    msg = "No user found with given phone number"
                    logger.debug(f"❌ Error: {msg}")
                    return create_response(msg, response_status=status.HTTP_400_BAD_REQUEST)
                if not verify_phone(phone):
                    msg = "The phone number have more than one account, contact system admin"
                    logger.debug(f"❌ Error: {msg}")
                    return create_response(msg, response_status=status.HTTP_400_BAD_REQUEST)

                user = get_user_phone(phone)
                otp_util = OtpUtil(user)

                if not otp_util.verify_otp_max_time():
                    msg = "Too many OTP attempts. Try again later. (after 10 minutes)"
                    logger.debug(f"❌ Error: {msg}")
                    return create_response(msg, status.HTTP_400_BAD_REQUEST)

                if not otp_util.verify_otp_expiry():
                    msg = "OTP expired"
                    logger.debug(f"❌ Error: {msg}")
                    return create_response(msg=msg, response_status=status.HTTP_400_BAD_REQUEST)

                if otp_util.check_max_limit():
                    msg = "Incorrect OTP. Too many attempts. Please try again after 5 minutes."
                    logger.debug(f"❌ Error: {msg}")
                    return create_response(msg, status.HTTP_400_BAD_REQUEST)

                if not otp_util.verify_otp(otp_code):
                    msg = otp_util.decrease_max_retries()
                    logger.debug(f"❌ Error: {msg}")
                    return create_response(f"{msg}", status.HTTP_400_BAD_REQUEST)

                if not check_password_match(password, confirm_password):
                    msg = "Please make sure two password match."
                    logger.debug(f"❌ Error: {msg}")
                    return create_response(msg, status.HTTP_400_BAD_REQUEST)

                change_user_password(user, password)

                msg = "Password reset successfully"
                return create_response(msg, status.HTTP_200_OK)
            else:
                logger.debug(f"❌ Error resetting password{serializer.errors}")
                msg = f"Invalid request body {serializer.errors}"
                return create_response(msg, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            msg = f"Server Error: {e}"
            return create_response(msg, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangeUserPasswordApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: {"msg": "Password changed successfully"},
            400: "Bad request - Invalid data, incorrect current password, or password mismatch",
        },
        tags=["auth"],
        summary="Change user password",
        description="Allows an authenticated user to change their password."
    )
    def post(self, request, *args, **kwargs):
        """
             Change password for the authenticated user.
             Payload: { "old_password": "...", "password": "...", "confirm_password": "..." }
        """
        serializer = ChangePasswordSerializer(data=request.data)
        old_password = request.data.get("old_password")
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if not serializer.is_valid():
            logger.debug(f"❌ invalid data: {serializer.errors}")
            msg = f"Invalid data: {serializer.errors}"
            return create_response(msg, status.HTTP_400_BAD_REQUEST)

        if not check_current_password(request.user, old_password):
            logger.debug("❌ Invalid current password")
            msg = "Invalid current password"
            return create_response(msg, status.HTTP_400_BAD_REQUEST)

        if not check_password_match(password, confirm_password):
            logger.debug("❌ password does not match")
            msg = "Passwords do not match"
            return create_response(msg, status.HTTP_400_BAD_REQUEST)

        change_user_password(request.user, password)
        logger.debug("✅ Password changed successfully")
        msg = "Password changed successfully"
        return create_response(msg, status.HTTP_200_OK)

# example to check permissions
# class CustomerOrderAPIView(APIView):
#     # default permission (won't be used if get_permissions is overridden)
#     permission_classes = []
#
#     def get_permissions(self):
#         """
#         Assign different permissions depending on HTTP method
#         """
#         if self.request.method == 'GET':
#             permission = ViewPermission
#             permission.model = CustomerOrder
#             return [permission()]
#         elif self.request.method == 'POST':
#             permission = AddPermission
#             permission.model = CustomerOrder
#             return [permission()]
#         return super().get_permissions()
#
#     def get(self, request, *args, **kwargs):
#         # Logic to list customer orders
#         return Response({"msg": "Orders retrieved"}, status=status.HTTP_200_OK)
#
#     def post(self, request, *args, **kwargs):
#         # Logic to create a customer order
#         return Response({"msg": "Customer order created"}, status=status.HTTP_201_CREATED)
