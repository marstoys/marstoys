import requests
import random
from decouple import config
from users.models import UserOtp, CustomUser as User
from rest_framework_simplejwt.tokens import RefreshToken
from core.exceptions.exception import CustomApiException
from core.exceptions.error_messages import ErrorCodes




def send_otp_via_sms(phone_number):
    
    otp = str(random.randint(10000, 99999))
    UserOtp.objects.create(phone_number=phone_number, otp_code=otp)

    url = "https://notify.eskiz.uz/api/message/sms/send"
    headers = {
        "Authorization": f"Bearer {config('ESKIZ_API_TOKEN')}"
    }
    payload = {
        "mobile_phone": phone_number,
        "message": f"Mars Toys websaytiga kirish uchun tasdiqlash kodingiz: {otp}",
        "from": "4546",
        "callback_url": "http://0000.uz/test.php"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(response.json())
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        print(requests.exceptions.RequestException)
        return False


def verify_otp(phone_number, otp):

    cached_otp = UserOtp.objects.filter(phone_number=phone_number, otp_code=otp, is_verified=False).first()

    if cached_otp is None:
        raise CustomApiException(ErrorCodes.OTP_EXPIRED,message="OTP muddati tugagan yoki mavjud emas.")

    if cached_otp.otp_code != otp:
        raise CustomApiException(ErrorCodes.INVALID_INPUT,message="Xato kod terdingiz.")

    user= User.objects.filter(phone_number=phone_number).first()
    if user is None:
        user = User.objects.create(phone_number=phone_number)

    cached_otp.is_verified = True
    cached_otp.save()

    refresh = RefreshToken.for_user(user)
    return {
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh)
    }