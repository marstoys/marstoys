from users.services.user_otp import send_otp_via_sms,verify_otp
from users.services.get_user_profile import get_user_profile
from users.models import CustomUser as User
from rest_framework.permissions import  AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers, status
from core.exceptions.exception import CustomApiException
from core.exceptions.error_messages import ErrorCodes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class UserProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(max_length=30, required=False)
    last_name = serializers.CharField(max_length=30, required=False)
    phone_number = serializers.CharField(max_length=15, required=False)
    address = serializers.CharField(max_length=255, required=False)

class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()

class TokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new user",
        operation_summary="User Registration",
        request_body=PhoneNumberSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response("OTP sent successfully."),
            status.HTTP_400_BAD_REQUEST: openapi.Response("Invalid input.")
        }
    )
    def post(self, request):
        phone_number = request.data.get('phone_number')

        if not phone_number:
            raise CustomApiException(ErrorCodes.INVALID_INPUT, message="Telefon raqam topilmadi.")

        if not send_otp_via_sms(phone_number):
            raise CustomApiException(ErrorCodes.INVALID_INPUT, message="SMS yuborishda xatolik yuz berdi.")

        return Response({"message": "OTP muvaffaqiyatli yuborildi"}, status=status.HTTP_200_OK)

class VerifyOTPAndRegisterView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_description="Verify OTP and register the user",
        operation_summary="Verify OTP",
        request_body=VerifyOTPSerializer,
        responses={
            status.HTTP_200_OK: TokenSerializer,
            status.HTTP_400_BAD_REQUEST: openapi.Response("Invalid input or OTP."),
            status.HTTP_404_NOT_FOUND: openapi.Response("User not found.")
        }
    )

    def post(self, request):
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')

        if not phone_number or not otp:
            raise CustomApiException(ErrorCodes.INVALID_INPUT, message="Telefon raqam va OTP talab qilinadi.")

        response=verify_otp(phone_number, otp)
        return Response(response, status=status.HTTP_200_OK)
        
class UserProfileAPIView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_description="Retrieve the profile of the authenticated user",
        operation_summary="Get User Profile",
        responses={
            status.HTTP_200_OK: UserProfileSerializer,
            status.HTTP_404_NOT_FOUND: openapi.Response("User profile not found.")
        }
    )

    def get(self, request):
        user_id = request.user.id 
        if not user_id:
            raise CustomApiException(ErrorCodes.USER_DOES_NOT_EXIST, message="Foydalanuvchi topilmadi.")

        profile = get_user_profile(user_id)
        if not profile:
            raise CustomApiException(ErrorCodes.USER_DOES_NOT_EXIST, message="Foydalanuvchi profili topilmadi.")

        serializer = UserProfileSerializer(profile) 
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserUpdateAPIView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_description="Update the profile of the authenticated user",
        operation_summary="Update User Profile",
        request_body=UserProfileSerializer,
        responses={
            status.HTTP_200_OK: UserProfileSerializer,
            status.HTTP_400_BAD_REQUEST: openapi.Response("Invalid input."),
            status.HTTP_404_NOT_FOUND: openapi.Response("User not found.")
        }
    )
    def put(self, request):
        user_id = request.user.id
        data = request.data

        user = User.objects.get(id=user_id)

        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.phone_number = data.get('phone', user.phone_number)
        user.address = data.get('address', user.address)

        user.save()

        profile = get_user_profile(user.id)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

