from users.services.user_otp import send_otp_via_sms,verify_otp
from users.services.get_user_profile import get_user_profile
from users.models import CustomUser as User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers, status
from core.exceptions.exception import CustomApiException
from core.exceptions.error_messages import ErrorCodes

class UserProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(max_length=30, required=False)
    last_name = serializers.CharField(max_length=30, required=False)
    phone_number = serializers.CharField(max_length=15, required=False)
    address = serializers.CharField(max_length=255, required=False)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get('phone_number')

        if not phone_number:
            raise CustomApiException(ErrorCodes.INVALID_INPUT, message="Telefon raqam topilmadi.")

        if not send_otp_via_sms(phone_number):
            raise CustomApiException(ErrorCodes.INVALID_INPUT, message="SMS yuborishda xatolik yuz berdi.")

        return Response({"message": "OTP muvaffaqiyatli yuborildi"}, status=200)

class VerifyOTPAndRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')

        if not phone_number or not otp:
            raise CustomApiException(ErrorCodes.INVALID_INPUT, message="Telefon raqam va OTP talab qilinadi.")

        response=verify_otp(phone_number, otp)
        return Response(response, status=200)
        
class UserProfileAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        user_id = request.user.id
        if not user_id:
            raise CustomApiException(ErrorCodes.USER_DOES_NOT_EXIST, message="Foydalanuvchi topilmadi.")
        profile = get_user_profile(user_id)
        if not profile:
            raise CustomApiException(ErrorCodes.USER_DOES_NOT_EXIST, message="Foydalanuvchi profili topilmadi.")
        serializer = UserProfileSerializer(data=profile)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserUpdateAPIView(APIView):
    permission_classes = [AllowAny]
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
        serializer = UserProfileSerializer(data=profile)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

