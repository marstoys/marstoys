import requests
import random
from core.constants import get_eskiz_token
from users.models import UserOtp, CustomUser as User
from rest_framework_simplejwt.tokens import RefreshToken
from core.exceptions.exception import CustomApiException
from core.exceptions.error_messages import ErrorCodes
from sms_service.models import SMSToken



def send_otp_via_sms(phone_number):
    otp = str(random.randint(10000, 99999))
    UserOtp.objects.create(phone_number=phone_number, otp_code=otp)

    eskiz_api_token = SMSToken.objects.filter(is_active=True).first()
    if not eskiz_api_token:
        token = get_eskiz_token()
    else:
        token = eskiz_api_token.token

    url = "https://notify.eskiz.uz/api/message/sms/send"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "mobile_phone": phone_number,
        "message": f"Mars Toys websaytiga kirish uchun tasdiqlash kodingiz: {otp}",
        "from": "4546",
        "callback_url": "http://0000.uz/test.php"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        if data.get("message") == "Expired":
            new_token = get_eskiz_token()
            headers["Authorization"] = f"Bearer {new_token}"
            response = requests.post(url, json=payload, headers=headers)
            print("Token yangilandi va SMS qayta yuborildi:", response.json())

        response.raise_for_status()
        return True

    except requests.exceptions.RequestException as e:
        print("Xatolik:", e)
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
    print(user)

    cached_otp.is_verified = True
    cached_otp.save()

    refresh = RefreshToken.for_user(user)
    return {
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh)
    }