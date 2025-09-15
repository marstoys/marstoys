import requests
import random
from decouple import config
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from core.exceptions.exception import CustomApiException
from core.exceptions.error_messages import ErrorCodes
User = get_user_model()



def send_otp_via_sms(phone_number):
    
    
    otp = str(random.randint(10000, 99999))
    cache.set(f"otp_{phone_number}", otp, timeout=300)

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
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False


def verify_otp(phone_number, otp):
    
    cached_otp = cache.get(f"otp_{phone_number}")

    if cached_otp is None:
        raise CustomApiException(ErrorCodes.OTP_EXPIRED,message="OTP muddati tugagan yoki mavjud emas.")

    if cached_otp != otp:
        raise CustomApiException(ErrorCodes.INVALID_OTP,message="Xato kod terdingiz.")

    user, _ = User.objects.get_or_create(phone_number=phone_number)

    cache.delete(f"otp_{phone_number}")

    refresh = RefreshToken.for_user(user)
    return {
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh)
    }