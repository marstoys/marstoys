from users.services.user_otp import send_otp_via_sms,verify_otp
from users.services.get_user_profile import get_user_profile
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from core.exceptions.exception import CustomApiException
from core.exceptions.error_messages import ErrorCodes
User = get_user_model()



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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        if not user_id:
            raise CustomApiException(ErrorCodes.USER_DOES_NOT_EXIST, message="Foydalanuvchi topilmadi.")
        profile = get_user_profile(user_id)
        if not profile:
            raise CustomApiException(ErrorCodes.USER_DOES_NOT_EXIST, message="Foydalanuvchi profili topilmadi.")
        return Response(profile, status=200)
        
        
        

