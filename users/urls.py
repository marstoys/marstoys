from django.urls import path
from rest_framework_simplejwt.views import  TokenRefreshView
from users.views import  *

urlpatterns = [
    path('login/', VerifyOTPAndRegisterView.as_view(), name='token_obtain_pair'),
    path('token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileAPIView.as_view(), name='profile'),
]
