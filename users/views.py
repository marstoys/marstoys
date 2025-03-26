import random

import requests
from decouple import config
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializer import RegisterSerializer, UserUpdateSerializer

User = get_user_model()


# Create your views here.

# class CustomTokenObtainPairView(TokenObtainPairView):
#     def post(self, request, *args, **kwargs):
#         try:
#             response = super().post(request, *args, **kwargs)
#             tokens = response.data
#             access_token = tokens['access']
#             refresh_token = tokens['refresh']
#             res = Response({'success': True})
#             res.set_cookie(key='access_token', value=access_token, httponly=True, secure=True, samesite='None',
#                            path='/')
#             res.set_cookie(key='refresh_token', value=refresh_token, httponly=True, secure=True, samesite='None',
#                            path='/')
#             return res
#         except Exception as e:
#             return Response({'success': False}, status=400)
#
#
# class CustomTokenRefreshView(TokenRefreshView):
#     def post(self, request, *args, **kwargs):
#         try:
#             refresh_token = request.COOKIES.get('refresh_token')
#             request.data['refresh'] = refresh_token
#             response = super().post(request, *args, **kwargs)
#             tokens = response.data
#             access_token = tokens['access']
#             res = Response({'refreshed': True})
#             res.set_cookie(
#                 key='access_token',
#                 value=access_token,
#                 httponly=True,
#                 secure=True,
#                 samesite='None',
#                 path='/'
#             )
#             return res
#         except:
#             return Response({'success': False}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=400)

        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({"success": True, "message": "Logged out successfully"}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    phone_number = request.data.get('phone_number')

    if not phone_number:
        return Response({"message": "Telefon raqam topilmadi."}, status=400)

    otp = str(random.randint(10000, 99999))
    cache.set(f"otp_{phone_number}", otp, timeout=300)

    if not send_otp_via_sms(phone_number, otp):
        return Response({"message": "SMS yuborishda xatolik yuz berdi."}, status=500)

    return Response({"message": "OTP muvaffaqiyatli yuborildi"}, status=200)


def send_otp_via_sms(phone, otp):
    url = "https://notify.eskiz.uz/api/message/sms/send"
    headers = {
        "Authorization": f"Bearer {config('ESKIZ_API_TOKEN')}"
    }
    payload = {
        "mobile_phone": phone,
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


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp_and_register(request):
    phone_number = request.data.get('phone_number')
    otp = request.data.get('otp')

    if not phone_number or not otp:
        return Response({"error": "Telefon raqam va OTP talab qilinadi"}, status=400)

    cached_otp = cache.get(f"otp_{phone_number}")

    if cached_otp is None:
        return Response({"message": "Siz 5 daqiqa ichida kodni kiritishingiz lozim edi."}, status=400)

    if cached_otp != otp:
        return Response({"message": "Xato kod terdingiz."}, status=400)

    user, created = User.objects.get_or_create(phone_number=phone_number)

    if created:
        serializer = RegisterSerializer(user, data={"phone_number": phone_number}, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=400)

    cache.delete(f"otp_{phone_number}")

    refresh = RefreshToken.for_user(user)
    return Response({
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh)
    }, status=200)


class UserProfileAPIView(RetrieveAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def is_authenticated(request):
    return Response({'authenticated': True})

